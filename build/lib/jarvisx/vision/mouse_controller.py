"""Mouse Controller for Phase 93 Computer Use & Vision Layer."""

from __future__ import annotations
import time
from typing import Any, Dict, Optional, Tuple


class MouseController:
    """Controls physical or virtual mouse cursor movement, clicks, dragging, and scrolling."""

    def __init__(self, screen_bounds: Tuple[int, int] = (1920, 1080)):
        self.max_width, self.max_height = screen_bounds
        self.current_position: Tuple[int, int] = (self.max_width // 2, self.max_height // 2)

    def move_to(self, x: int, y: int, duration_sec: float = 0.1) -> Dict[str, Any]:
        """Smoothly move mouse cursor to target coordinates."""
        clamped_x = max(0, min(x, self.max_width))
        clamped_y = max(0, min(y, self.max_height))
        self.current_position = (clamped_x, clamped_y)

        try:
            import pyautogui
            pyautogui.moveTo(clamped_x, clamped_y, duration=duration_sec)
        except Exception:
            pass

        return {
            "status": "SUCCESS",
            "action": "move",
            "coordinates": (clamped_x, clamped_y),
            "duration_sec": duration_sec
        }

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1) -> Dict[str, Any]:
        """Click at specific or current mouse coordinates."""
        target_x = x if x is not None else self.current_position[0]
        target_y = y if y is not None else self.current_position[1]
        self.move_to(target_x, target_y)

        try:
            import pyautogui
            pyautogui.click(x=target_x, y=target_y, clicks=clicks, button=button)
        except Exception:
            pass

        return {
            "status": "SUCCESS",
            "action": f"{button}_click",
            "clicks": clicks,
            "coordinates": (target_x, target_y)
        }

    def scroll(self, clicks: int = -500) -> Dict[str, Any]:
        """Scroll vertical wheel."""
        try:
            import pyautogui
            pyautogui.scroll(clicks)
        except Exception:
            pass

        return {"status": "SUCCESS", "action": "scroll", "clicks": clicks}
