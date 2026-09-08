"""
Windows Power & Keep-Awake Guard for Jarvis X.
Prevents operating system sleep, monitor standby, and idle power saving
during long-running autonomous execution using direct Win32 kernel32 APIs.
"""
from __future__ import annotations

import ctypes
import logging
import sys
from typing import Optional

logger = logging.getLogger("jarvisx.power_guard")

# Win32 Execution State Flags
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
ES_USER_PRESENT = 0x00000004
ES_AWAYMODE_REQUIRED = 0x00000040
ES_CONTINUOUS = 0x80000000


class KeepAwakeGuard:
    """Context manager and controller to prevent Windows sleep during missions."""

    def __init__(self, mission_name: str = "autonomous_task", keep_display_awake: bool = True):
        self.mission_name = mission_name
        self.keep_display_awake = keep_display_awake
        self.is_windows = (sys.platform == "win32")
        self._active = False
        self._prev_state: Optional[int] = None

    @property
    def is_active(self) -> bool:
        return self._active

    def activate(self) -> bool:
        """Asserts system and display execution requirements to block sleep."""
        if not self.is_windows:
            self._active = True
            logger.debug(f"[PowerGuard] Non-Windows platform ({sys.platform}); state marked active.")
            return True

        flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
        if self.keep_display_awake:
            flags |= ES_DISPLAY_REQUIRED

        try:
            kernel32 = ctypes.windll.kernel32
            # Calling SetThreadExecutionState returns the previous state on success, or 0 on error
            res = kernel32.SetThreadExecutionState(flags)
            if res != 0:
                self._prev_state = res
                self._active = True
                logger.info(f"[PowerGuard] Keep-Awake asserted for mission '{self.mission_name}' (flags: 0x{flags:08X}).")
                return True
            else:
                logger.warning(f"[PowerGuard] SetThreadExecutionState failed for mission '{self.mission_name}'.")
                return False
        except Exception as e:
            logger.error(f"[PowerGuard] Error setting thread execution state: {e}")
            return False

    def deactivate(self) -> bool:
        """Restores default Windows power management."""
        if not self.is_windows:
            self._active = False
            return True

        if not self._active:
            return True

        try:
            kernel32 = ctypes.windll.kernel32
            # Re-asserting ES_CONTINUOUS without ES_SYSTEM_REQUIRED clears the requirement
            res = kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            self._active = False
            logger.info(f"[PowerGuard] Keep-Awake released for mission '{self.mission_name}'; power management restored.")
            return bool(res != 0)
        except Exception as e:
            logger.error(f"[PowerGuard] Error releasing execution state: {e}")
            return False

    def __enter__(self) -> KeepAwakeGuard:
        self.activate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deactivate()
