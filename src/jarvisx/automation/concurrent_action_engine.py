"""
Concurrent Action Engine — Mid-Sentence Tool Execution for Alfred OS
====================================================================
Enables Jarvis X to speak and execute tools SIMULTANEOUSLY.

Instead of the sequential flow:
    Brain decides → Tool executes (BLOCKING) → Then speaks

This engine enables:
    Brain decides → Speech starts immediately → Tool fires mid-utterance

Architecture:
    ┌──────────────────────────────────────────────────┐
    │  ConcurrentActionEngine.execute_with_speech()    │
    │                                                  │
    │  ┌─────────────┐       ┌──────────────────┐     │
    │  │  TTS Thread  │  ←→  │  Action Thread    │     │
    │  │  (non-block) │       │  (tool executor) │     │
    │  └─────────────┘       └──────────────────┘     │
    │         ↓                       ↓               │
    │   Speech plays           Tool runs              │
    │   concurrently           mid-sentence            │
    └──────────────────────────────────────────────────┘
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("jarvisx.concurrent_action")


# ── Trigger Modes ──
class TriggerMode(Enum):
    """When to fire the tool relative to speech."""
    IMMEDIATE = "immediate"       # Tool fires at the same instant speech begins
    MID_SENTENCE = "mid_sentence" # Tool fires after ~40-60% of estimated speech duration
    ON_KEYWORD = "on_keyword"     # Tool fires when a specific action word would be spoken


# ── Result Container ──
@dataclass
class ConcurrentResult:
    """Result of concurrent speech + action execution."""
    speech_text: str = ""
    tool_name: str = ""
    tool_args: Dict[str, Any] = field(default_factory=dict)
    tool_result: Optional[Dict[str, Any]] = None
    tool_error: Optional[str] = None
    speech_started_at: float = 0.0
    tool_fired_at: float = 0.0
    tool_completed_at: float = 0.0
    total_duration_ms: float = 0.0
    concurrent: bool = True

    @property
    def overlap_ms(self) -> float:
        """How many milliseconds of overlap between speech and tool execution."""
        if self.speech_started_at and self.tool_fired_at:
            return max(0, (self.tool_fired_at - self.speech_started_at) * 1000)
        return 0.0

    @property
    def tool_succeeded(self) -> bool:
        return self.tool_result is not None and self.tool_result.get("status") == "success"


# ── Destructive Tool Safeguard ──
DESTRUCTIVE_TOOLS = frozenset({
    "delete_file", "remove_file", "format_disk", "rm_rf",
    "drop_database", "truncate_table", "factory_reset",
    "uninstall_app", "wipe_data", "shutdown_system",
})


class ConcurrentActionEngine:
    """
    Coordinates parallel speech + tool execution for mid-sentence actions.

    Usage:
        engine = ConcurrentActionEngine(mouth=organism.mouth, hands=organism.hands)
        result = await engine.execute_with_speech(
            speech_text="Opening VS Code for you right now, Sir.",
            tool_name="open_app",
            tool_args={"application": "code"},
            trigger_mode=TriggerMode.MID_SENTENCE,
        )
    """

    # Average speaking rate: ~150 words/minute = ~400ms per word
    WORD_DURATION_MS = 400

    def __init__(
        self,
        mouth: Any = None,
        hands: Any = None,
        on_tool_error: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        self.mouth = mouth
        self.hands = hands
        self.on_tool_error = on_tool_error
        self._active_threads: List[threading.Thread] = []

    def _estimate_speech_duration_ms(self, text: str) -> float:
        """Estimate how long TTS will take to speak the text."""
        word_count = len(text.split())
        return word_count * self.WORD_DURATION_MS

    def _compute_trigger_delay_ms(
        self,
        speech_text: str,
        trigger_mode: TriggerMode,
        trigger_keyword: Optional[str] = None,
    ) -> float:
        """Calculate delay before firing the tool action."""
        if trigger_mode == TriggerMode.IMMEDIATE:
            return 0.0

        estimated_duration = self._estimate_speech_duration_ms(speech_text)

        if trigger_mode == TriggerMode.MID_SENTENCE:
            # Fire at ~40% through the speech for natural feel
            return estimated_duration * 0.4

        if trigger_mode == TriggerMode.ON_KEYWORD and trigger_keyword:
            words = speech_text.lower().split()
            keyword_lower = trigger_keyword.lower()
            for i, word in enumerate(words):
                if keyword_lower in word:
                    # Fire when this word would be spoken
                    return i * self.WORD_DURATION_MS
            # Keyword not found, fall back to mid-sentence
            return estimated_duration * 0.4

        return 0.0

    def _is_destructive(self, tool_name: str) -> bool:
        """Check if a tool is destructive and should NOT use concurrent mode."""
        return tool_name.lower() in DESTRUCTIVE_TOOLS

    async def execute_with_speech(
        self,
        speech_text: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        trigger_mode: TriggerMode = TriggerMode.MID_SENTENCE,
        trigger_keyword: Optional[str] = None,
    ) -> ConcurrentResult:
        """
        Execute speech and tool action concurrently.

        The speech begins playing immediately. The tool fires after a calculated
        delay based on the trigger mode, creating the illusion that Jarvis is
        performing the action mid-sentence.

        Args:
            speech_text: What to say while acting
            tool_name: Tool to execute
            tool_args: Arguments for the tool
            trigger_mode: When to fire the tool relative to speech
            trigger_keyword: Word in speech that triggers tool (for ON_KEYWORD mode)

        Returns:
            ConcurrentResult with timing data and tool output
        """
        t0 = time.perf_counter()
        result = ConcurrentResult(
            speech_text=speech_text,
            tool_name=tool_name,
            tool_args=tool_args,
        )

        # Safety: destructive tools fall back to sequential execution
        if self._is_destructive(tool_name):
            logger.warning(f"[ConcurrentAction] Destructive tool '{tool_name}' — falling back to sequential")
            result.concurrent = False
            tool_output = self.hands.act(tool_name, tool_args)
            result.tool_result = tool_output
            result.tool_fired_at = time.perf_counter()
            result.tool_completed_at = time.perf_counter()
            if self.mouth and speech_text:
                self.mouth.speak(speech_text, blocking=False)
                result.speech_started_at = time.perf_counter()
            result.total_duration_ms = (time.perf_counter() - t0) * 1000
            return result

        # Calculate when to fire the tool
        delay_ms = self._compute_trigger_delay_ms(speech_text, trigger_mode, trigger_keyword)
        delay_sec = delay_ms / 1000.0

        # ── Thread-safe containers ──
        tool_output_container: Dict[str, Any] = {}
        tool_error_container: Dict[str, str] = {}
        tool_timing: Dict[str, float] = {}

        def _run_tool():
            """Execute tool in background thread after delay."""
            try:
                if delay_sec > 0:
                    time.sleep(delay_sec)

                tool_timing["fired_at"] = time.perf_counter()
                logger.info(
                    f"[ConcurrentAction] 🦾 Firing '{tool_name}' mid-sentence "
                    f"(delay={delay_ms:.0f}ms, mode={trigger_mode.value})"
                )

                output = self.hands.act(tool_name, tool_args)
                tool_output_container.update(output)
                tool_timing["completed_at"] = time.perf_counter()

                logger.info(
                    f"[ConcurrentAction] ✓ Tool '{tool_name}' completed in "
                    f"{(tool_timing['completed_at'] - tool_timing['fired_at']) * 1000:.0f}ms"
                )

            except Exception as e:
                tool_error_container["error"] = str(e)
                tool_timing["completed_at"] = time.perf_counter()
                logger.error(f"[ConcurrentAction] ✗ Tool '{tool_name}' failed: {e}")

                # Queue a correction speech if tool fails
                if self.on_tool_error:
                    self.on_tool_error(tool_name, str(e))

        # ── Launch both concurrently ──

        # 1. Start the tool thread (it will sleep for delay_sec then execute)
        tool_thread = threading.Thread(
            target=_run_tool,
            daemon=True,
            name=f"MidSentenceAction-{tool_name}",
        )
        self._active_threads.append(tool_thread)
        tool_thread.start()

        # 2. Start speech immediately (non-blocking)
        result.speech_started_at = time.perf_counter()
        if self.mouth and speech_text:
            self.mouth.speak(speech_text, blocking=False)
            logger.info(f"[ConcurrentAction] 🗣️ Speech started: \"{speech_text[:60]}...\"")

        # 3. Wait for tool thread to complete (with timeout)
        tool_thread.join(timeout=30.0)

        # ── Collect results ──
        result.tool_fired_at = tool_timing.get("fired_at", 0.0)
        result.tool_completed_at = tool_timing.get("completed_at", 0.0)

        if tool_error_container:
            result.tool_error = tool_error_container["error"]
            result.tool_result = {"status": "failed", "error": result.tool_error}
        else:
            result.tool_result = tool_output_container

        result.total_duration_ms = (time.perf_counter() - t0) * 1000

        # Clean up
        if tool_thread in self._active_threads:
            self._active_threads.remove(tool_thread)

        logger.info(
            f"[ConcurrentAction] 🏁 Concurrent execution complete: "
            f"total={result.total_duration_ms:.0f}ms, "
            f"speech_to_tool_gap={result.overlap_ms:.0f}ms, "
            f"tool_status={'✓' if result.tool_succeeded else '✗'}"
        )

        return result

    async def execute_speech_only(self, speech_text: str) -> None:
        """Speak without any tool action (pure conversation response)."""
        if self.mouth and speech_text:
            self.mouth.speak(speech_text, blocking=False)

    def cancel_all(self) -> None:
        """Cancel any pending action threads."""
        for t in self._active_threads:
            if t.is_alive():
                logger.warning(f"[ConcurrentAction] Cancelling thread: {t.name}")
        self._active_threads.clear()
