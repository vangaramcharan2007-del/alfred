"""Window Detector — identifies the active application window."""
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class WindowDetector:
    """Detects active window title and executable."""

    @classmethod
    def get_active_window(cls) -> Tuple[str, str]:
        """Returns (window_title, executable_name) of the active window."""
        try:
            import pygetwindow as gw
            window = gw.getActiveWindow()
            if window and window.title:
                title = window.title
                # Heuristic for executable since pygetwindow doesn't reliably give exe name
                exe = "Unknown.exe"
                if "Visual Studio Code" in title:
                    title = "Visual Studio Code"
                    exe = "Code.exe"
                elif "Chrome" in title or "Google Chrome" in title:
                    title = "Google Chrome"
                    exe = "chrome.exe"
                elif "Notepad" in title:
                    exe = "notepad.exe"
                return title, exe
            return "", ""
        except ImportError:
            logger.warning("pygetwindow is not installed.")
            return "", ""
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return "", ""
