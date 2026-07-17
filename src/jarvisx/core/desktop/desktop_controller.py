"""Desktop Controller — provides primitive GUI actions (typing, clicking, shortcuts)."""
import logging
import time

logger = logging.getLogger(__name__)

class DesktopController:
    """Handles keyboard and mouse interaction using pyautogui."""
    
    def __init__(self):
        try:
            import pyautogui
            self.pa = pyautogui
            # Fail-safe: moving mouse to corner aborts
            self.pa.FAILSAFE = True
            # Add a tiny delay between actions to improve reliability
            self.pa.PAUSE = 0.1
            self.available = True
        except ImportError:
            self.available = False
            logger.warning("pyautogui is not installed. Desktop actions will fail.")

    def type_text(self, text: str, interval: float = 0.01) -> bool:
        """Type a string of text into the active window."""
        if not self.available:
            return False
        try:
            self.pa.write(text, interval=interval)
            return True
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False

    def press_shortcut(self, keys: str) -> bool:
        """Press a keyboard shortcut (e.g. 'ctrl s', 'alt tab', 'enter')."""
        if not self.available:
            return False
        try:
            # Parse keys: 'ctrl s' -> ['ctrl', 's']
            parsed_keys = keys.split()
            self.pa.hotkey(*parsed_keys)
            return True
        except Exception as e:
            logger.error(f"Failed to press shortcut '{keys}': {e}")
            return False

    def scroll(self, direction: str, amount: int = 500) -> bool:
        """Scroll the active window up or down."""
        if not self.available:
            return False
        try:
            if direction.lower() == "up":
                self.pa.scroll(amount)
            elif direction.lower() == "down":
                self.pa.scroll(-amount)
            else:
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")
            return False

    def click(self, x: int = None, y: int = None) -> bool:
        """Click the mouse at the current position or (x, y)."""
        if not self.available:
            return False
        try:
            if x is not None and y is not None:
                self.pa.click(x=x, y=y)
            else:
                self.pa.click()
            return True
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return False
