"""
Deterministic Native Windows Desktop Driver for Jarvis X.
Uses in-memory Win32 API and pywinauto UIA backend for sub-15ms execution,
eliminating slow PowerShell process spawning and blind pixel clicking.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import logging
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from jarvisx.harness.aov_engine import (
    AOVResult,
    ClosedLoopHarness,
    StateObserver,
    rule_any_state_delta,
    rule_window_title_contains,
)

logger = logging.getLogger("jarvisx.desktop_driver")

# Win32 Mouse Event Flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_ABSOLUTE = 0x8000

# Win32 Key Event Flags
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004


@dataclass
class DesktopElement:
    name: str
    control_type: str
    automation_id: str
    rect: Dict[str, int]
    is_enabled: bool
    is_visible: bool
    native_handle: int


class DeterministicDesktopDriver:
    """High-performance in-memory Windows desktop automation driver."""

    _instance: Optional[DeterministicDesktopDriver] = None

    @classmethod
    def get_instance(cls) -> DeterministicDesktopDriver:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.is_windows = (sys.platform == "win32")
        self.harness = ClosedLoopHarness(max_retries=2, retry_delay_sec=0.2)
        self._uia_app = None

    # -----------------------------------------------------------------------
    # Direct In-Memory Win32 Primitives (<1ms)
    # -----------------------------------------------------------------------

    def move_cursor_instant(self, x: int, y: int) -> bool:
        if not self.is_windows:
            return False
        return bool(ctypes.windll.user32.SetCursorPos(x, y))

    def mouse_click_instant(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left") -> bool:
        if not self.is_windows:
            return False
        if x is not None and y is not None:
            self.move_cursor_instant(x, y)
            time.sleep(0.01)

        down_flag = MOUSEEVENTF_LEFTDOWN if button == "left" else MOUSEEVENTF_RIGHTDOWN
        up_flag = MOUSEEVENTF_LEFTUP if button == "left" else MOUSEEVENTF_RIGHTUP

        ctypes.windll.user32.mouse_event(down_flag, 0, 0, 0, 0)
        time.sleep(0.01)
        ctypes.windll.user32.mouse_event(up_flag, 0, 0, 0, 0)
        return True

    def double_click_instant(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        self.mouse_click_instant(x, y, "left")
        time.sleep(0.05)
        self.mouse_click_instant(x, y, "left")
        return True

    def type_string_instant(self, text: str) -> bool:
        """Types string directly using Win32 SendInput Unicode events."""
        if not self.is_windows:
            return False
        user32 = ctypes.windll.user32
        for char in text:
            code = ord(char)
            user32.keybd_event(0, code, KEYEVENTF_UNICODE, 0)
            user32.keybd_event(0, code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0)
            time.sleep(0.005)
        return True

    def set_foreground_window(self, hwnd: int) -> bool:
        """Focuses window and brings to front via Win32."""
        if not self.is_windows:
            return False
        user32 = ctypes.windll.user32
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        return bool(user32.SetForegroundWindow(hwnd))

    # -----------------------------------------------------------------------
    # Native Windows UI Automation (UIA) Semantic Tree Resolution
    # -----------------------------------------------------------------------

    def find_window_by_query(self, title_query: str) -> Optional[int]:
        """Finds top-level HWND matching partial title."""
        if not self.is_windows:
            return None
        target_hwnd: Optional[int] = None
        user32 = ctypes.windll.user32

        def callback(hwnd, extra):
            nonlocal target_hwnd
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    if title_query.lower() in buff.value.strip().lower():
                        target_hwnd = hwnd
                        return False  # Stop enumeration
            return True

        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(EnumWindowsProc(callback), 0)
        return target_hwnd

    def find_elements_uia(
        self,
        window_title: str,
        name: Optional[str] = None,
        control_type: Optional[str] = None,
        auto_id: Optional[str] = None,
    ) -> List[DesktopElement]:
        """Inspects window using pywinauto UIA backend."""
        elements: List[DesktopElement] = []
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="uia")
            window = desktop.window(title_re=f".*{window_title}.*")
            if not window.exists(timeout=1.0):
                return []

            criteria = {}
            if name:
                criteria["title_re"] = f".*{name}.*"
            if control_type:
                criteria["control_type"] = control_type
            if auto_id:
                criteria["auto_id"] = auto_id

            matches = window.descendants(**criteria) if criteria else window.descendants()
            for m in matches[:25]:
                try:
                    r = m.rectangle()
                    rect_dict = {"left": r.left, "top": r.top, "right": r.right, "bottom": r.bottom, "width": r.width(), "height": r.height()}
                    elements.append(
                        DesktopElement(
                            name=m.window_text(),
                            control_type=m.element_info.control_type,
                            automation_id=m.element_info.automation_id or "",
                            rect=rect_dict,
                            is_enabled=m.is_enabled(),
                            is_visible=m.is_visible(),
                            native_handle=m.handle,
                        )
                    )
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"[DesktopDriver] UIA element search note: {e}")

        return elements

    # -----------------------------------------------------------------------
    # Closed-Loop Verified Desktop Actions (AOV Engine Integrated)
    # -----------------------------------------------------------------------

    def focus_window_verified(self, title_query: str) -> AOVResult:
        """Focuses a window and verifies foreground window changed."""
        hwnd = self.find_window_by_query(title_query)
        if not hwnd:
            # Create synthetic failure result
            pre = StateObserver.capture()
            diff = StateObserver.compute_diff(pre, pre)
            return AOVResult(
                action_name=f"FocusWindow({title_query})",
                success=False,
                verification_status="FAILED",
                pre_state=pre,
                post_state=pre,
                diff=diff,
                action_output=None,
                verification_reason=f"Window matching '{title_query}' was not found.",
                error="WindowNotFound",
            )

        def act():
            return self.set_foreground_window(hwnd)

        rule = rule_window_title_contains(title_query)
        return self.harness.execute_closed_loop(
            action_name=f"FocusWindow({title_query})",
            act_fn=act,
            rules=[rule],
        )

    def click_element_verified(self, x: int, y: int) -> AOVResult:
        """Clicks at coordinates and verifies state delta."""
        def act():
            return self.mouse_click_instant(x, y, "left")

        return self.harness.execute_closed_loop(
            action_name=f"ClickCoordinates({x}, {y})",
            act_fn=act,
            rules=[rule_any_state_delta()],
        )

    def type_text_verified(self, text: str) -> AOVResult:
        """Types text into active window and verifies state transition."""
        def act():
            return self.type_string_instant(text)

        return self.harness.execute_closed_loop(
            action_name=f"TypeText(len={len(text)})",
            act_fn=act,
            rules=[rule_any_state_delta()],
        )
