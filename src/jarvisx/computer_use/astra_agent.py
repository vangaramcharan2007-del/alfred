"""
ASTRA — Alfred's Screen-to-Action Real-time Agent
==================================================
Gemini Vision-driven closed-loop computer use engine.

Pipeline:
  1. CAPTURE  — Full-screen screenshot via mss (fast, zero-lag)
  2. PERCEIVE — Gemini Flash vision reads screen, returns structured JSON plan
  3. ACT      — pyautogui executes mouse/keyboard actions
  4. OBSERVE  — Re-capture screen, verify goal completion
  5. LOOP     — Repeat until task is done or max_steps reached

This is Alfred's answer to GPT-6 Astra: real Gemini vision + real OS control.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

logger = logging.getLogger("jarvisx.astra")

# ── Safe lazy imports ────────────────────────────────────────────────────────
try:
    import mss
    import mss.tools
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    logger.warning("mss not installed — screen capture disabled. pip install mss")

try:
    from PIL import ImageGrab as _PILGrab
    PIL_GRAB_AVAILABLE = True
except ImportError:
    PIL_GRAB_AVAILABLE = False

try:
    import pyautogui
    pyautogui.FAILSAFE = True   # Move mouse to top-left to emergency-stop
    pyautogui.PAUSE   = 0.08   # Small inter-action delay
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.warning("pyautogui not installed — mouse/keyboard control disabled. pip install pyautogui")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from google import genai as _genai
    from google.genai import types as _genai_types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai not installed. pip install google-genai")


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class AstraAction:
    action_type: Literal[
        "click", "double_click", "right_click",
        "type_text", "hotkey", "scroll",
        "drag", "screenshot_only", "done", "fail"
    ]
    x: Optional[int]          = None
    y: Optional[int]          = None
    text: Optional[str]       = None
    keys: Optional[List[str]] = None   # e.g. ["ctrl", "c"]
    scroll_dy: Optional[int]  = None   # positive = down
    drag_to: Optional[Tuple[int, int]] = None
    reasoning: str            = ""


@dataclass
class AstraStep:
    step: int
    screenshot_b64: str         # base64 PNG of what was seen
    action: AstraAction
    result_status: str          = "pending"   # success | failed | done
    observation: str            = ""
    duration_ms: float          = 0.0


@dataclass
class AstraMission:
    mission_id: str
    goal: str
    steps: List[AstraStep]      = field(default_factory=list)
    final_status: str           = "RUNNING"
    total_duration_ms: float    = 0.0
    success: bool               = False
    summary: str                = ""


# ── Core Engine ──────────────────────────────────────────────────────────────

class AstraAgent:
    """
    Gemini Vision-driven autonomous computer-use agent.

    Usage:
        agent = AstraAgent(api_key="YOUR_GEMINI_KEY")
        mission = await agent.run("Open Chrome and search for SRM CGPA calculator")
        print(mission.summary)
    """

    GEMINI_VISION_MODEL = "gemini-2.0-flash"

    # System prompt given to Gemini on every turn
    SYSTEM_PROMPT = """You are ASTRA, an autonomous computer-use agent controlling a Windows desktop.
You see screenshots and must decide the SINGLE NEXT ACTION to accomplish the user's goal.

Respond ONLY with valid JSON (no markdown, no code fences):
{
  "action_type": "<one of: click|double_click|right_click|type_text|hotkey|scroll|drag|screenshot_only|done|fail>",
  "x": <pixel x coordinate or null>,
  "y": <pixel y coordinate or null>,
  "text": "<text to type or null>",
  "keys": ["ctrl","c"] or null,
  "scroll_dy": <positive=down, negative=up, or null>,
  "drag_to": [x2, y2] or null,
  "reasoning": "<brief thought explaining why this action>"
}

Rules:
- Use "done" when the goal is fully accomplished. Include a summary in "reasoning".
- Use "fail" only if the goal is impossible (e.g. app not installed).
- Coordinates must be exact pixel positions visible in the screenshot.
- Prefer clicking visible UI elements over keyboard shortcuts where possible.
- After type_text always observe the result before the next action.
- Never click outside visible screen boundaries.
"""

    def __init__(
        self,
        api_key: Optional[str]   = None,
        max_steps: int           = 15,
        capture_dir: Optional[Path] = None,
        verbose: bool            = True,
    ):
        self.api_key     = api_key or os.getenv("GEMINI_API_KEY", "")
        self.max_steps   = max_steps
        self.capture_dir = capture_dir or Path("var/runtime/astra_captures")
        self.verbose     = verbose
        self.capture_dir.mkdir(parents=True, exist_ok=True)

        if GENAI_AVAILABLE and self.api_key:
            self._client = _genai.Client(api_key=self.api_key)
        else:
            self._client = None

        # Track screen resolution
        if PYAUTOGUI_AVAILABLE:
            self.screen_w, self.screen_h = pyautogui.size()
        else:
            self.screen_w, self.screen_h = 1920, 1080

    # ── Screenshot ─────────────────────────────────────────────────────────

    def capture_screen(self, save: bool = False) -> Tuple[bytes, str]:
        """
        Captures full screen, returns (png_bytes, base64_string).

        Priority order (most reliable on Windows desktop):
          1. pyautogui.screenshot() — uses pywin32 GDI, most robust
          2. PIL ImageGrab.grab()   — standard PIL approach
          3. mss.MSS()             — fastest, multi-monitor
        """
        import io

        png_bytes = None

        # Primary: pyautogui (most reliable from a real desktop session)
        if PYAUTOGUI_AVAILABLE:
            try:
                img = pyautogui.screenshot()
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                png_bytes = buf.getvalue()
            except Exception as e:
                logger.debug(f"pyautogui screenshot failed: {e}")

        # Secondary: PIL ImageGrab
        if png_bytes is None and PIL_GRAB_AVAILABLE:
            try:
                img = _PILGrab.grab()
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                png_bytes = buf.getvalue()
            except Exception as e:
                logger.debug(f"PIL grab failed: {e}")

        # Tertiary: mss
        if png_bytes is None and MSS_AVAILABLE:
            try:
                with mss.MSS() as sct:
                    monitor = sct.monitors[1]  # primary monitor
                    raw = sct.grab(monitor)
                    png_bytes = mss.tools.to_png(raw.rgb, raw.size)
            except Exception as e:
                logger.error(f"mss grab failed: {e}")

        if png_bytes is None:
            raise RuntimeError(
                "All screen capture methods failed. "
                "Run ASTRA from your own terminal (not a background shell)."
            )

        b64 = base64.b64encode(png_bytes).decode("utf-8")

        if save:
            ts = int(time.time() * 1000)
            path = self.capture_dir / f"screen_{ts}.png"
            path.write_bytes(png_bytes)
            logger.debug(f"Screenshot saved: {path}")

        return png_bytes, b64

    # ── Vision Reasoning ───────────────────────────────────────────────────

    async def _ask_gemini(self, goal: str, screenshot_b64: str, history: List[str]) -> AstraAction:
        """
        Sends screenshot to Gemini Flash vision and gets the next action.
        """
        if not self._client:
            logger.error("Gemini client not initialised — check GEMINI_API_KEY")
            return AstraAction(action_type="fail", reasoning="Gemini API not configured.")

        history_block = "\n".join(history[-6:]) if history else "No prior actions."
        user_prompt = (
            f"GOAL: {goal}\n\n"
            f"SCREEN RESOLUTION: {self.screen_w}x{self.screen_h}\n\n"
            f"RECENT ACTIONS:\n{history_block}\n\n"
            "Look at the screenshot and decide the SINGLE NEXT action. "
            "Reply with the JSON schema described in your system prompt."
        )

        loop = asyncio.get_event_loop()

        def _call_api():
            response = self._client.models.generate_content(
                model=self.GEMINI_VISION_MODEL,
                contents=[
                    _genai_types.Part.from_text(self.SYSTEM_PROMPT + "\n\n" + user_prompt),
                    _genai_types.Part.from_bytes(
                        data=base64.b64decode(screenshot_b64),
                        mime_type="image/png",
                    ),
                ],
                config=_genai_types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=512,
                ),
            )
            return response.text.strip()

        raw = ""
        try:
            raw = await loop.run_in_executor(None, _call_api)
            # Strip markdown fences if model adds them
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()
            data = json.loads(raw)
            return AstraAction(
                action_type  = data.get("action_type", "screenshot_only"),
                x            = data.get("x"),
                y            = data.get("y"),
                text         = data.get("text"),
                keys         = data.get("keys"),
                scroll_dy    = data.get("scroll_dy"),
                drag_to      = tuple(data["drag_to"]) if data.get("drag_to") else None,
                reasoning    = data.get("reasoning", ""),
            )
        except Exception as exc:
            logger.error(f"Gemini parse error: {exc} | raw={raw[:200]}")
            return AstraAction(action_type="screenshot_only", reasoning=f"Parse error: {exc}")

    # ── Action Executor ────────────────────────────────────────────────────

    def _execute_action(self, action: AstraAction) -> Dict[str, Any]:
        """Dispatches the action to pyautogui / OS."""
        if not PYAUTOGUI_AVAILABLE:
            return {"status": "simulated", "action": action.action_type}

        try:
            at = action.action_type

            if at == "click":
                pyautogui.click(action.x, action.y)
                return {"status": "success", "action": "click", "at": (action.x, action.y)}

            elif at == "double_click":
                pyautogui.doubleClick(action.x, action.y)
                return {"status": "success", "action": "double_click", "at": (action.x, action.y)}

            elif at == "right_click":
                pyautogui.rightClick(action.x, action.y)
                return {"status": "success", "action": "right_click", "at": (action.x, action.y)}

            elif at == "type_text":
                pyautogui.typewrite(action.text or "", interval=0.04)
                return {"status": "success", "action": "type_text", "text": action.text}

            elif at == "hotkey":
                if action.keys:
                    pyautogui.hotkey(*action.keys)
                return {"status": "success", "action": "hotkey", "keys": action.keys}

            elif at == "scroll":
                pyautogui.scroll(action.scroll_dy or -3, x=action.x, y=action.y)
                return {"status": "success", "action": "scroll", "dy": action.scroll_dy}

            elif at == "drag":
                if action.drag_to and action.x is not None and action.y is not None:
                    pyautogui.moveTo(action.x, action.y, duration=0.3)
                    pyautogui.dragTo(*action.drag_to, duration=0.5, button="left")
                return {"status": "success", "action": "drag"}

            elif at in ("screenshot_only", "done", "fail"):
                return {"status": "success", "action": at}

            return {"status": "unknown_action", "action": at}

        except Exception as exc:
            logger.error(f"Action execution error: {exc}")
            return {"status": "error", "error": str(exc)}

    # ── Main Loop ──────────────────────────────────────────────────────────

    async def run(self, goal: str) -> AstraMission:
        """
        Execute a natural-language computer-use goal end-to-end.

        Args:
            goal: Natural language task, e.g. "Open YouTube and search for lo-fi music"

        Returns:
            AstraMission with all steps, final status, and summary.
        """
        mission_id = f"astra_{int(time.time() * 1000)}"
        mission = AstraMission(mission_id=mission_id, goal=goal)
        history: List[str] = []
        start_t = time.time()

        self._log(f"\n{'='*60}")
        self._log(f"  ASTRA MISSION START")
        self._log(f"  Goal: {goal}")
        self._log(f"{'='*60}")

        for step_num in range(1, self.max_steps + 1):
            step_t0 = time.time()
            self._log(f"\n[Step {step_num}/{self.max_steps}] Capturing screen...")

            # 1. CAPTURE
            try:
                _, b64 = self.capture_screen(save=(step_num == 1))
            except Exception as exc:
                self._log(f"  CAPTURE ERROR: {exc}")
                break

            # 2. PERCEIVE — ask Gemini what to do
            self._log(f"  Asking Gemini Vision...")
            action = await self._ask_gemini(goal, b64, history)
            self._log(f"  ACTION: {action.action_type.upper()} | {action.reasoning}")

            if action.x and action.y:
                self._log(f"  TARGET:  ({action.x}, {action.y})")
            if action.text:
                self._log(f"  TEXT:    {action.text!r}")
            if action.keys:
                self._log(f"  KEYS:    {'+'.join(action.keys)}")

            # 3. ACT
            result = self._execute_action(action)
            self._log(f"  RESULT:  {result}")

            # 4. OBSERVE — small pause then re-screenshot for observation
            await asyncio.sleep(0.8)
            step_duration = round((time.time() - step_t0) * 1000, 1)

            step = AstraStep(
                step          = step_num,
                screenshot_b64= b64,
                action        = action,
                result_status = result.get("status", "unknown"),
                observation   = action.reasoning,
                duration_ms   = step_duration,
            )
            mission.steps.append(step)

            # Track history for context
            history.append(
                f"Step {step_num}: {action.action_type}"
                + (f" @ ({action.x},{action.y})" if action.x else "")
                + (f" text={action.text!r}" if action.text else "")
                + (f" keys={action.keys}" if action.keys else "")
                + f" — {action.reasoning[:80]}"
            )

            # 5. CHECK TERMINAL STATE
            if action.action_type == "done":
                mission.final_status = "COMPLETED"
                mission.success = True
                mission.summary = action.reasoning
                self._log(f"\n  MISSION COMPLETE: {action.reasoning}")
                break

            if action.action_type == "fail":
                mission.final_status = "FAILED"
                mission.success = False
                mission.summary = action.reasoning
                self._log(f"\n  MISSION FAILED: {action.reasoning}")
                break

        else:
            mission.final_status = "MAX_STEPS_REACHED"
            mission.summary = f"Reached {self.max_steps} steps without completing goal."
            self._log(f"\n  MAX STEPS REACHED.")

        mission.total_duration_ms = round((time.time() - start_t) * 1000, 1)
        self._log(f"\n{'='*60}")
        self._log(f"  STATUS: {mission.final_status} | {len(mission.steps)} steps | {mission.total_duration_ms:.0f}ms")
        self._log(f"{'='*60}\n")

        return mission

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)
        logger.info(msg)

    # ── Sync wrapper ───────────────────────────────────────────────────────

    def run_sync(self, goal: str) -> AstraMission:
        """Synchronous wrapper for non-async callers."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self.run(goal))
                    return future.result()
        except RuntimeError:
            pass
        return asyncio.run(self.run(goal))


# ── Convenience factory ───────────────────────────────────────────────────────

def get_astra(api_key: Optional[str] = None, max_steps: int = 15) -> AstraAgent:
    """Return a configured AstraAgent."""
    return AstraAgent(
        api_key   = api_key or os.getenv("GEMINI_API_KEY"),
        max_steps = max_steps,
        verbose   = True,
    )
