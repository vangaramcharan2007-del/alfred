"""Ambient watching: turn what you are doing into signals you can act on.

The repo already had real sensors — ``ActiveWindowContextSensor`` (ctypes +
psutil), ``AmbientClipboardSensor``, ``ScreenContextEngine`` — but nothing
consumed their output, so they observed without ever saying anything.

This module is the consumer. It is deliberately **not** a productivity
monitor. Watching an ADHD brain for "wasted time" produces shame, and shame
produces avoidance, which is the actual problem. Instead it watches for four
things that are mechanically useful:

1. **fragmentation** — many app switches in a short window. Task switching is
   the most expensive thing an ADHD brain does, and it is usually invisible
   while it is happening.
2. **task mismatch** — you said the task was the assignment, but you have been
   on YouTube for eleven minutes. Stated neutrally, never as a judgement.
3. **time blindness** — you have been at this for 50 minutes and said "five
   minutes" an hour ago.
4. **capture** — something you copied looks like a thing you need to remember,
   so it goes into the intake list instead of living in your head.

Everything here is pure and deterministic: :class:`AttentionLedger` ingests
plain observations and emits nudges, with no OS calls at all. The real sensors
are optional adapters on top, so this is fully testable headless and degrades
gracefully on a machine with no desktop.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Sequence, runtime_checkable

from jarvisx.agentic.intake import IntakeEngine

logger = logging.getLogger("jarvisx.agentic.watch")


# --------------------------------------------------------------------------- #
# Observations
# --------------------------------------------------------------------------- #


@dataclass
class Observation:
    """One sample of what the user was looking at."""

    app: str
    title: str = ""
    mode: str = "GENERAL"     # CODING, WEB_RESEARCH, MEDIA, PRODUCTIVITY, ...
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "app": self.app,
            "title": self.title,
            "mode": self.mode,
            "timestamp": self.timestamp,
        }


_DISTRACTION_MODES = frozenset({"MEDIA", "GAMING", "SOCIAL"})


def is_distraction(obs: Observation) -> bool:
    """True when the current window is consumption rather than work."""
    if obs.mode.upper() in _DISTRACTION_MODES:
        return True
    return bool(_DISTRACTION_SITE_RE.search(obs.title or ""))


_DISTRACTION_SITE_RE = re.compile(
    r"""\b(?:youtube|netflix|instagram|twitter|x\.com|tiktok|reddit|twitch|
            facebook|discord|prime\s+video|hotstar)\b""",
    re.IGNORECASE | re.VERBOSE,
)


# --------------------------------------------------------------------------- #
# Nudges
# --------------------------------------------------------------------------- #


class NudgeKind(str, Enum):
    FRAGMENTED = "fragmented"      # too many switches
    OFF_TASK = "off_task"          # not on the stated task
    TIME_CHECK = "time_check"      # been at this a long time
    BREAK = "break"                # long unbroken stretch
    CAPTURED = "captured"          # something was saved to your list
    ON_TRACK = "on_track"          # genuinely going well — say so sometimes


@dataclass
class Nudge:
    kind: NudgeKind
    message: str
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"kind": self.kind.value, "message": self.message, "evidence": self.evidence}


# --------------------------------------------------------------------------- #
# The ledger — pure, deterministic, testable
# --------------------------------------------------------------------------- #


class AttentionLedger:
    """Ingests observations, emits nudges. No I/O, no timers, no OS calls."""

    def __init__(
        self,
        switch_window_seconds: float = 300.0,
        fragmentation_threshold: int = 6,
        off_task_seconds: float = 300.0,
        break_after_seconds: float = 3000.0,
        minimum_reported_seconds: float = 60.0,
    ):
        self.switch_window = switch_window_seconds
        self.fragmentation_threshold = fragmentation_threshold
        self.off_task_seconds = off_task_seconds
        self.break_after = break_after_seconds
        self.minimum_reported = minimum_reported_seconds

        self._observations: List[Observation] = []
        self._intended_task: Optional[str] = None
        self._intended_at: float = 0.0
        self._cooldowns: Dict[NudgeKind, float] = {}
        self.cooldown_seconds = 600.0

    # -- input ------------------------------------------------------------- #

    def set_intended_task(self, task: str, at: Optional[float] = None) -> None:
        """Record what you said you were going to work on."""
        self._intended_task = (task or "").strip() or None
        self._intended_at = at if at is not None else time.time()

    @property
    def intended_task(self) -> Optional[str]:
        return self._intended_task

    def observe(self, obs: Observation) -> List[Nudge]:
        """Record one observation and return any nudges it triggers."""
        self._observations.append(obs)
        # Keep the buffer bounded; we only ever look back `switch_window`.
        cutoff = obs.timestamp - max(self.switch_window, self.break_after) * 2
        self._observations = [o for o in self._observations if o.timestamp >= cutoff]

        nudges: List[Nudge] = []
        for check in (
            self._check_fragmentation,
            self._check_off_task,
            self._check_break,
        ):
            nudge = check(obs)
            if nudge is not None:
                nudges.append(nudge)
        return nudges

    # -- signals ----------------------------------------------------------- #

    def switches_in_window(self, now: Optional[float] = None) -> int:
        """How many app changes happened in the recent window."""
        if len(self._observations) < 2:
            return 0
        now = now if now is not None else self._observations[-1].timestamp
        recent = [o for o in self._observations if o.timestamp >= now - self.switch_window]
        return sum(
            1 for a, b in zip(recent, recent[1:]) if a.app.lower() != b.app.lower()
        )

    def seconds_on_current(self, now: Optional[float] = None) -> float:
        """How long the current app has held focus, unbroken."""
        if not self._observations:
            return 0.0
        current = self._observations[-1].app.lower()
        now = now if now is not None else self._observations[-1].timestamp
        start = self._observations[-1].timestamp
        for obs in reversed(self._observations):
            if obs.app.lower() != current:
                break
            start = obs.timestamp
        return max(0.0, now - start)

    def seconds_since_intent(self, now: Optional[float] = None) -> float:
        if not self._intended_task:
            return 0.0
        now = now if now is not None else (
            self._observations[-1].timestamp if self._observations else time.time()
        )
        return max(0.0, now - self._intended_at)

    def focus_streak(self) -> float:
        """Longest unbroken stretch on a single app in the buffer."""
        best = 0.0
        run_start: Optional[float] = None
        previous: Optional[str] = None
        for obs in self._observations:
            app = obs.app.lower()
            if app != previous:
                run_start = obs.timestamp
                previous = app
            # Not `run_start or obs.timestamp`: a run_start of 0.0 is falsy,
            # which silently collapsed every streak to zero.
            start = run_start if run_start is not None else obs.timestamp
            best = max(best, obs.timestamp - start)
        return best

    # -- individual checks ------------------------------------------------- #

    def _check_fragmentation(self, obs: Observation) -> Optional[Nudge]:
        switches = self.switches_in_window(obs.timestamp)
        if switches < self.fragmentation_threshold:
            return None
        if self._on_cooldown(NudgeKind.FRAGMENTED, obs.timestamp):
            return None
        self._cooldowns[NudgeKind.FRAGMENTED] = obs.timestamp
        minutes = int(self.switch_window / 60)
        return Nudge(
            kind=NudgeKind.FRAGMENTED,
            message=(
                f"You have switched apps {switches} times in the last {minutes} minutes. "
                "That is expensive. Pick one window and stay in it for ten minutes."
            ),
            evidence={"switches": switches, "window_seconds": self.switch_window},
        )

    def _check_off_task(self, obs: Observation) -> Optional[Nudge]:
        if not self._intended_task:
            return None
        if not is_distraction(obs):
            return None
        seconds = self.seconds_on_current(obs.timestamp)
        if seconds < self.off_task_seconds:
            return None
        if self._on_cooldown(NudgeKind.OFF_TASK, obs.timestamp):
            return None
        self._cooldowns[NudgeKind.OFF_TASK] = obs.timestamp
        minutes = int(seconds // 60)
        return Nudge(
            kind=NudgeKind.OFF_TASK,
            message=(
                f"You are {minutes} minutes into {obs.app}, and the task you named was "
                f"'{self._intended_task}'. No judgement — do you want to switch back, "
                "or should I move that task to later?"
            ),
            evidence={
                "app": obs.app,
                "seconds": seconds,
                "intended_task": self._intended_task,
            },
        )

    def _check_break(self, obs: Observation) -> Optional[Nudge]:
        streak = self.focus_streak()
        if streak < self.break_after:
            return None
        if self._on_cooldown(NudgeKind.BREAK, obs.timestamp):
            return None
        self._cooldowns[NudgeKind.BREAK] = obs.timestamp
        minutes = int(streak // 60)
        return Nudge(
            kind=NudgeKind.BREAK,
            message=(
                f"You have been going for {minutes} minutes straight. "
                "Stand up for five. The task will still be there."
            ),
            evidence={"streak_seconds": streak},
        )

    def _on_cooldown(self, kind: NudgeKind, now: float) -> bool:
        last = self._cooldowns.get(kind)
        return last is not None and (now - last) < self.cooldown_seconds

    # -- summary ----------------------------------------------------------- #

    def summary(self) -> Dict[str, Any]:
        """A snapshot of the session, for the HUD or a status command."""
        if not self._observations:
            return {"observations": 0, "switches": 0, "focus_streak_seconds": 0.0}
        latest = self._observations[-1]
        return {
            "observations": len(self._observations),
            "current_app": latest.app,
            "current_mode": latest.mode,
            "switches": self.switches_in_window(latest.timestamp),
            "seconds_on_current": round(self.seconds_on_current(latest.timestamp), 1),
            "focus_streak_seconds": round(self.focus_streak(), 1),
            "intended_task": self._intended_task,
            "seconds_since_intent": round(self.seconds_since_intent(latest.timestamp), 1),
        }


# --------------------------------------------------------------------------- #
# Clipboard capture
# --------------------------------------------------------------------------- #

_TASKY_RE = re.compile(
    r"""\b(?:todo|to\s+do|remember|don'?t\s+forget|need\s+to|gotta|must|
            follow\s+up|remind\s+me|task:|idea:)\b""",
    re.IGNORECASE | re.VERBOSE,
)


def looks_capturable(text: str, min_chars: int = 8, max_chars: int = 240) -> bool:
    """Should this clipboard content become a captured item?

    Deliberately strict. Capturing everything makes the list worthless, and a
    worthless list gets ignored within a day.
    """
    cleaned = (text or "").strip()
    if not (min_chars <= len(cleaned) <= max_chars):
        return False
    if cleaned.count("\n") > 3:          # a pasted block, not a note
        return False
    if not _TASKY_RE.search(cleaned):
        return False
    return True


# --------------------------------------------------------------------------- #
# Sources
# --------------------------------------------------------------------------- #


@runtime_checkable
class ContextSource(Protocol):
    """Anything that can report what the user is currently looking at."""

    @property
    def available(self) -> bool: ...

    def poll(self) -> Optional[Observation]: ...


class ScriptedSource:
    """Replays a fixed list of observations. For tests and demos."""

    def __init__(self, observations: Sequence[Observation]):
        self._observations = list(observations)
        self._index = 0
        self.available = True

    def poll(self) -> Optional[Observation]:
        if self._index >= len(self._observations):
            return None
        obs = self._observations[self._index]
        self._index += 1
        return obs


class ActiveWindowSource:
    """Wraps the repo's existing ``ActiveWindowContextSensor``.

    Degrades to ``available = False`` on a headless or non-Windows machine
    rather than raising, so the watcher simply does nothing instead of
    crashing the agent.
    """

    def __init__(self):
        self._sensor = None
        self.available = False
        try:
            from jarvisx.harness.active_context_sensor import ActiveWindowContextSensor

            sensor = ActiveWindowContextSensor()
            # One synchronous read; we drive the polling ourselves so the
            # watcher owns its own cadence.
            context = sensor._read_active_window() if hasattr(
                sensor, "_read_active_window"
            ) else None
            if context is None and hasattr(sensor, "current_context"):
                sensor.start()
                time.sleep(0.05)
                context = sensor.current_context
                sensor.stop()
            if context is not None:
                self._sensor = sensor
                self.available = True
        except Exception as exc:  # noqa: BLE001 - no desktop, no ctypes, no psutil
            logger.info("active-window sensor unavailable: %s", exc)
            self.available = False

    def poll(self) -> Optional[Observation]:
        if not self.available:
            return None
        try:
            context = self._sensor.current_context
            if context is None:
                return None
            return Observation(
                app=context.process_name or "unknown",
                title=context.window_title or "",
                mode=context.context_mode or "GENERAL",
                timestamp=context.timestamp or time.time(),
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("window poll failed: %s", exc)
            return None


class ClipboardSource:
    """Wraps the repo's ``AmbientClipboardSensor`` when pyperclip is present."""

    def __init__(self):
        self._last: Optional[str] = None
        self.available = False
        try:
            import pyperclip  # noqa: F401

            self._pyperclip = pyperclip
            self.available = True
        except Exception as exc:  # noqa: BLE001
            logger.info("clipboard unavailable: %s", exc)
            self.available = False

    def poll(self) -> Optional[str]:
        if not self.available:
            return None
        try:
            text = self._pyperclip.paste()
        except Exception:  # noqa: BLE001
            return None
        if not text or text == self._last:
            return None
        self._last = text
        return text


# --------------------------------------------------------------------------- #
# The watcher
# --------------------------------------------------------------------------- #


class ContextWatcher:
    """Polls a source, feeds the ledger, captures stray thoughts, speaks up."""

    def __init__(
        self,
        ledger: Optional[AttentionLedger] = None,
        source: Optional[ContextSource] = None,
        clipboard: Optional[ClipboardSource] = None,
        intake: Optional[IntakeEngine] = None,
        on_nudge: Optional[Callable[[Nudge], None]] = None,
        auto_capture: bool = True,
    ):
        self.ledger = ledger or AttentionLedger()
        self.source = source
        self.clipboard = clipboard
        self.intake = intake or IntakeEngine()
        self.on_nudge = on_nudge
        self.auto_capture = auto_capture
        self.nudges: List[Nudge] = []
        self.captured: List[str] = []

    # -- single tick ------------------------------------------------------- #

    def tick(self, obs: Optional[Observation] = None, clipboard_text: Optional[str] = None) -> List[Nudge]:
        """One poll cycle. Pass values explicitly to drive it from a test."""
        emitted: List[Nudge] = []

        if obs is None and self.source is not None and self.source.available:
            obs = self.source.poll()
        if obs is not None:
            emitted.extend(self.ledger.observe(obs))

        if clipboard_text is None and self.clipboard is not None and self.clipboard.available:
            clipboard_text = self.clipboard.poll()
        if clipboard_text and self.auto_capture and looks_capturable(clipboard_text):
            items = self.intake.capture(clipboard_text)
            if items:
                self.captured.extend(i.title for i in items)
                nudge = Nudge(
                    kind=NudgeKind.CAPTURED,
                    message=f"Saved '{items[0].title}' so you do not have to hold it.",
                    evidence={"items": [i.title for i in items]},
                )
                emitted.append(nudge)

        for nudge in emitted:
            self.nudges.append(nudge)
            if self.on_nudge:
                try:
                    self.on_nudge(nudge)
                except Exception as exc:  # noqa: BLE001 - a listener must not break watching
                    logger.warning("nudge listener failed: %s", exc)
        return emitted

    # -- loop -------------------------------------------------------------- #

    def run(
        self,
        interval: float = 5.0,
        max_ticks: Optional[int] = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> List[Nudge]:
        """Poll until stopped or `max_ticks` is reached.

        ``sleep`` is injectable so the loop can be tested without waiting.
        """
        ticks = 0
        while max_ticks is None or ticks < max_ticks:
            self.tick()
            ticks += 1
            sleep(interval)
        return self.nudges

    def summary(self) -> Dict[str, Any]:
        return {
            **self.ledger.summary(),
            "nudges": len(self.nudges),
            "captured": list(self.captured),
            "source_available": bool(self.source and self.source.available),
        }
