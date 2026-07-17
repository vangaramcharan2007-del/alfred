"""Window Manager — handles window focus, switching, and closing."""
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class WindowManager:
    """Manages OS window state using pygetwindow."""

    def __init__(self):
        try:
            import pygetwindow
            self.gw = pygetwindow
            self.available = True
        except ImportError:
            self.available = False
            logger.warning("pygetwindow not installed. Window management will fail.")

    def get_windows(self) -> List[str]:
        """Returns a list of all visible window titles."""
        if not self.available:
            return []
        try:
            return [w.title for w in self.gw.getAllWindows() if w.title]
        except Exception as e:
            logger.error(f"Failed to list windows: {e}")
            return []

    def get_active_window(self) -> str:
        """Returns the title of the currently active window."""
        if not self.available:
            return ""
        try:
            win = self.gw.getActiveWindow()
            return win.title if win else ""
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return ""

    def activate_window(self, partial_title: str) -> bool:
        """Finds a window by partial title and brings it to focus."""
        if not self.available:
            return False
        try:
            windows = self.gw.getWindowsWithTitle(partial_title)
            if not windows:
                return False
            
            # Prefer visible windows
            for win in windows:
                if win.visible:
                    # Windows API quirks sometimes require minimizing/restoring to grab focus
                    try:
                        win.activate()
                    except Exception:
                        win.minimize()
                        win.restore()
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to activate window '{partial_title}': {e}")
            return False

    def close_window(self, partial_title: str) -> bool:
        """Closes a window matching the partial title."""
        if not self.available:
            return False
        try:
            windows = self.gw.getWindowsWithTitle(partial_title)
            if not windows:
                return False
            
            for win in windows:
                if win.visible:
                    win.close()
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to close window '{partial_title}': {e}")
            return False

    def close_active_window(self) -> bool:
        """Closes the currently active window."""
        if not self.available:
            return False
        try:
            win = self.gw.getActiveWindow()
            if win:
                win.close()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to close active window: {e}")
            return False
