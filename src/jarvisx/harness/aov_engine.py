"""
Act-Observe-Verify (AOV) Closed-Loop Execution Engine for Jarvis X.
Enforces deterministic pre-condition capture, action dispatch, post-condition observation,
state diffing, and rule-based verification to eliminate open-loop automation failures.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("jarvisx.aov_engine")


@dataclass
class WindowState:
    hwnd: int
    title: str
    process_name: str
    rect: Dict[str, int]
    is_active: bool


@dataclass
class StateSnapshot:
    """Deterministic snapshot of system and application state at a precise instant."""
    timestamp: float
    cursor_pos: Tuple[int, int]
    active_window: Optional[WindowState]
    clipboard_hash: str
    open_window_count: int
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "cursor_pos": list(self.cursor_pos),
            "active_window": asdict(self.active_window) if self.active_window else None,
            "clipboard_hash": self.clipboard_hash,
            "open_window_count": self.open_window_count,
            "custom_metrics": self.custom_metrics,
        }


@dataclass
class StateDiff:
    """Mathematical delta between Pre-action and Post-action snapshots."""
    elapsed_ms: float
    cursor_moved: bool
    cursor_delta: Tuple[int, int]
    window_changed: bool
    old_window_title: str
    new_window_title: str
    clipboard_changed: bool
    window_count_delta: int
    custom_diffs: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_any_change(self) -> bool:
        return (
            self.cursor_moved
            or self.window_changed
            or self.clipboard_changed
            or self.window_count_delta != 0
            or bool(self.custom_diffs)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "elapsed_ms": round(self.elapsed_ms, 2),
            "cursor_moved": self.cursor_moved,
            "cursor_delta": list(self.cursor_delta),
            "window_changed": self.window_changed,
            "old_window_title": self.old_window_title,
            "new_window_title": self.new_window_title,
            "clipboard_changed": self.clipboard_changed,
            "window_count_delta": self.window_count_delta,
            "custom_diffs": self.custom_diffs,
        }


class VerificationStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class VerificationRule:
    """Rule evaluated against StateDiff and Post-State."""
    name: str
    validator: Callable[[StateSnapshot, StateSnapshot, StateDiff], Tuple[bool, str]]


@dataclass
class AOVResult:
    """Complete diagnostic outcome of an AOV closed-loop action execution."""
    action_name: str
    success: bool
    verification_status: VerificationStatus
    pre_state: StateSnapshot
    post_state: StateSnapshot
    diff: StateDiff
    action_output: Any
    verification_reason: str
    retry_count: int = 0
    recovery_attempted: bool = False
    error: Optional[str] = None

    def summary(self) -> str:
        status_icon = "[PASS]" if self.success else "[FAIL]"
        return (
            f"{status_icon} Action '{self.action_name}' | Verification: {self.verification_status.value} "
            f"({self.verification_reason}) | Elapsed: {self.diff.elapsed_ms:.1f}ms | Retries: {self.retry_count}"
        )


class StateObserver:
    """Captures low-level Win32 / OS state snapshots with microsecond latency."""

    @staticmethod
    def get_cursor_pos() -> Tuple[int, int]:
        if sys.platform == "win32":
            pt = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return (pt.x, pt.y)
        return (0, 0)

    @staticmethod
    def get_active_window() -> Optional[WindowState]:
        if sys.platform != "win32":
            return None
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return None

            length = user32.GetWindowTextLengthW(hwnd)
            title = ""
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.strip()

            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top

            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            return WindowState(
                hwnd=hwnd,
                title=title,
                process_name=f"PID_{pid.value}",
                rect={"left": rect.left, "top": rect.top, "right": rect.right, "bottom": rect.bottom, "width": w, "height": h},
                is_active=True,
            )
        except Exception as e:
            logger.debug(f"Error reading active window: {e}")
            return None

    @staticmethod
    def get_clipboard_hash() -> str:
        if sys.platform != "win32":
            return ""
        try:
            import pyperclip
            text = pyperclip.paste()
            if text:
                return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:12]
        except Exception:
            pass
        return "empty_or_inaccessible"

    @staticmethod
    def count_open_windows() -> int:
        if sys.platform != "win32":
            return 0
        count = 0
        try:
            user32 = ctypes.windll.user32
            def callback(hwnd, extra):
                nonlocal count
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        count += 1
                return True
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
            user32.EnumWindows(EnumWindowsProc(callback), 0)
        except Exception:
            pass
        return count

    @classmethod
    def capture(cls, custom_metrics: Optional[Dict[str, Any]] = None) -> StateSnapshot:
        return StateSnapshot(
            timestamp=time.perf_counter(),
            cursor_pos=cls.get_cursor_pos(),
            active_window=cls.get_active_window(),
            clipboard_hash=cls.get_clipboard_hash(),
            open_window_count=cls.count_open_windows(),
            custom_metrics=custom_metrics or {},
        )

    @staticmethod
    def compute_diff(pre: StateSnapshot, post: StateSnapshot) -> StateDiff:
        elapsed_ms = (post.timestamp - pre.timestamp) * 1000.0
        cursor_dx = post.cursor_pos[0] - pre.cursor_pos[0]
        cursor_dy = post.cursor_pos[1] - pre.cursor_pos[1]
        cursor_moved = (cursor_dx != 0 or cursor_dy != 0)

        pre_title = pre.active_window.title if pre.active_window else ""
        post_title = post.active_window.title if post.active_window else ""
        window_changed = (
            (pre.active_window is None and post.active_window is not None)
            or (pre.active_window is not None and post.active_window is None)
            or (pre.active_window and post.active_window and pre.active_window.hwnd != post.active_window.hwnd)
            or (pre_title != post_title)
        )

        clipboard_changed = (pre.clipboard_hash != post.clipboard_hash)
        window_count_delta = post.open_window_count - pre.open_window_count

        custom_diffs = {}
        for k, v in post.custom_metrics.items():
            pre_v = pre.custom_metrics.get(k)
            if pre_v != v:
                custom_diffs[k] = {"before": pre_v, "after": v}

        return StateDiff(
            elapsed_ms=elapsed_ms,
            cursor_moved=cursor_moved,
            cursor_delta=(cursor_dx, cursor_dy),
            window_changed=window_changed,
            old_window_title=pre_title,
            new_window_title=post_title,
            clipboard_changed=clipboard_changed,
            window_count_delta=window_count_delta,
            custom_diffs=custom_diffs,
        )


# ---------------------------------------------------------------------------
# Pre-built Standard Verification Rules
# ---------------------------------------------------------------------------

def rule_window_title_contains(target_substring: str) -> VerificationRule:
    def validator(pre: StateSnapshot, post: StateSnapshot, diff: StateDiff) -> Tuple[bool, str]:
        if not post.active_window:
            return False, "No active window found after action."
        actual_title = post.active_window.title.lower()
        if target_substring.lower() in actual_title:
            return True, f"Active window title '{post.active_window.title}' matches '{target_substring}'."
        return False, f"Expected window containing '{target_substring}', but active window is '{post.active_window.title}'."
    return VerificationRule(name=f"WindowTitleContains({target_substring})", validator=validator)


def rule_clipboard_updated() -> VerificationRule:
    def validator(pre: StateSnapshot, post: StateSnapshot, diff: StateDiff) -> Tuple[bool, str]:
        if diff.clipboard_changed:
            return True, f"Clipboard hash changed from {pre.clipboard_hash} to {post.clipboard_hash}."
        return False, "Clipboard content did not change."
    return VerificationRule(name="ClipboardUpdated", validator=validator)


def rule_cursor_moved_to(expected_target: Tuple[int, int], tolerance: int = 5) -> VerificationRule:
    def validator(pre: StateSnapshot, post: StateSnapshot, diff: StateDiff) -> Tuple[bool, str]:
        dist = ((post.cursor_pos[0] - expected_target[0]) ** 2 + (post.cursor_pos[1] - expected_target[1]) ** 2) ** 0.5
        if dist <= tolerance:
            return True, f"Cursor placed at {post.cursor_pos} (within {tolerance}px of target {expected_target})."
        return False, f"Cursor at {post.cursor_pos}, expected {expected_target} (distance: {dist:.1f}px)."
    return VerificationRule(name=f"CursorMovedTo({expected_target})", validator=validator)


def rule_any_state_delta() -> VerificationRule:
    def validator(pre: StateSnapshot, post: StateSnapshot, diff: StateDiff) -> Tuple[bool, str]:
        if diff.has_any_change:
            return True, "Verified non-empty state delta."
        return False, "Zero state change detected in system (action had no effect)."
    return VerificationRule(name="AnyStateDelta", validator=validator)


def rule_custom_metric_equals(metric_key: str, expected_value: Any) -> VerificationRule:
    def validator(pre: StateSnapshot, post: StateSnapshot, diff: StateDiff) -> Tuple[bool, str]:
        actual = post.custom_metrics.get(metric_key)
        if actual == expected_value:
            return True, f"Metric '{metric_key}' matches expected '{expected_value}'."
        return False, f"Metric '{metric_key}' is '{actual}', expected '{expected_value}'."
    return VerificationRule(name=f"MetricEquals({metric_key}={expected_value})", validator=validator)


def rule_action_succeeded(description: str = "Action executed cleanly") -> VerificationRule:
    def validator(pre: StateSnapshot, post: StateSnapshot, diff: StateDiff) -> Tuple[bool, str]:
        return True, description
    return VerificationRule(name=f"ActionSucceeded({description})", validator=validator)


# ---------------------------------------------------------------------------
# Closed-Loop Executor Engine
# ---------------------------------------------------------------------------

class ClosedLoopHarness:
    """Executes atomic operations using the Act-Observe-Verify pattern."""

    def __init__(self, max_retries: int = 2, retry_delay_sec: float = 0.5):
        self.max_retries = max_retries
        self.retry_delay_sec = retry_delay_sec

    def execute_closed_loop(
        self,
        action_name: str,
        act_fn: Callable[[], Any],
        rules: Optional[List[VerificationRule]] = None,
        custom_observer: Optional[Callable[[], Dict[str, Any]]] = None,
        recovery_fn: Optional[Callable[[AOVResult], bool]] = None,
    ) -> AOVResult:
        """
        Executes action with deterministic pre/post snapshots, delta computation,
        and rule verification. Retries automatically on verification failure.
        """
        rules = rules or [rule_any_state_delta()]
        last_result: Optional[AOVResult] = None

        for attempt in range(self.max_retries + 1):
            custom_pre = custom_observer() if custom_observer else {}
            pre_state = StateObserver.capture(custom_metrics=custom_pre)

            action_output = None
            action_error = None
            try:
                action_output = act_fn()
            except Exception as e:
                action_error = str(e)
                logger.error(f"[AOV] Action '{action_name}' threw exception: {e}")

            time.sleep(0.05)  # Brief settling tick for OS message pump
            custom_post = custom_observer() if custom_observer else {}
            post_state = StateObserver.capture(custom_metrics=custom_post)

            diff = StateObserver.compute_diff(pre_state, post_state)

            verification_passed = True
            reasons: List[str] = []

            if action_error:
                verification_passed = False
                reasons.append(f"Execution Error: {action_error}")
            else:
                for rule in rules:
                    passed, reason = rule.validator(pre_state, post_state, diff)
                    reasons.append(f"{rule.name}: {reason}")
                    if not passed:
                        verification_passed = False
                        break

            ver_status = VerificationStatus.PASSED if verification_passed else VerificationStatus.FAILED
            combined_reason = "; ".join(reasons)

            last_result = AOVResult(
                action_name=action_name,
                success=verification_passed,
                verification_status=ver_status,
                pre_state=pre_state,
                post_state=post_state,
                diff=diff,
                action_output=action_output,
                verification_reason=combined_reason,
                retry_count=attempt,
                error=action_error,
            )

            if verification_passed:
                logger.info(f"[AOV] {last_result.summary()}")
                return last_result

            logger.warning(f"[AOV] Attempt {attempt + 1}/{self.max_retries + 1} failed: {combined_reason}")

            if recovery_fn and attempt < self.max_retries:
                logger.info(f"[AOV] Triggering recovery handler for '{action_name}'...")
                recovered = recovery_fn(last_result)
                last_result.recovery_attempted = True
                if not recovered:
                    logger.warning("[AOV] Recovery handler could not rectify state.")

            if attempt < self.max_retries:
                time.sleep(self.retry_delay_sec * (attempt + 1))

        return last_result
