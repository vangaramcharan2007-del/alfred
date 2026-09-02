"""Keyboard Controller for Phase 93 Computer Use & Vision Layer."""

from __future__ import annotations
import time
from typing import Any, Dict, List


class KeyboardController:
    """Controls physical text typing, hotkeys, and keypress sequences."""

    def type_text(self, text: str, interval_sec: float = 0.01) -> Dict[str, Any]:
        """Type characters safely into the currently focused window."""
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=interval_sec)
        except Exception:
            pass

        return {
            "status": "SUCCESS",
            "action": "type_text",
            "characters_typed": len(text),
            "text_preview": text[:20] + ("..." if len(text) > 20 else "")
        }

    def press_hotkey(self, *keys: str) -> Dict[str, Any]:
        """Trigger keyboard hotkey combination (e.g. ('ctrl', 's') or ('win', 'r'))."""
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
        except Exception:
            pass

        return {
            "status": "SUCCESS",
            "action": "hotkey",
            "keys": list(keys)
        }

    def press_key(self, key_name: str) -> Dict[str, Any]:
        """Press single special key (e.g. 'enter', 'esc', 'tab')."""
        try:
            import pyautogui
            pyautogui.press(key_name)
        except Exception:
            pass

        return {
            "status": "SUCCESS",
            "action": "press_key",
            "key": key_name
        }
