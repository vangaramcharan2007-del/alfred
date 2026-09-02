import time
from typing import Tuple, Optional
import logging

try:
    import pyautogui
except ImportError:
    pyautogui = None

logger = logging.getLogger("jarvisx.ev_hands")

class EVHands:
    """Agentic Computer Use Framework for E-V to autonomously control the OS."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "EVHands":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if pyautogui:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1

    def move_mouse(self, x: int, y: int):
        """Move mouse to specific coordinates."""
        if pyautogui:
            print(f"[E-V HANDS] Moving mouse to {x}, {y}")
            pyautogui.moveTo(x, y, duration=0.25)

    def click(self, x: Optional[int] = None, y: Optional[int] = None):
        """Click at current or specific coordinates."""
        if pyautogui:
            print(f"[E-V HANDS] Clicking at {x}, {y}")
            pyautogui.click(x, y)

    def type_text(self, text: str, interval: float = 0.02):
        """Autonomously type text character by character (Devin/Social Media style)."""
        if pyautogui:
            print(f"[E-V HANDS] Typing text: {text[:20]}...")
            pyautogui.typewrite(text, interval=interval)
            
    def press_hotkey(self, *keys):
        """Press OS hotkey combination."""
        if pyautogui:
            print(f"[E-V HANDS] Pressing hotkey: {keys}")
            pyautogui.hotkey(*keys)
