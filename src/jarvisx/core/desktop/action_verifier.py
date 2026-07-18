"""Action Verifier — verifies desktop actions and GUI states."""
import time
import logging
from jarvisx.core.desktop.window_manager import WindowManager

logger = logging.getLogger(__name__)

class ActionVerifier:
    """Verifies if an action successfully completed by checking OS state."""

    def __init__(self, window_manager: WindowManager):
        self.wm = window_manager

    def verify_window_active(self, expected_partial_title: str, timeout: float = 2.0) -> bool:
        """Wait until a window matching the title becomes active."""
        start = time.time()
        while time.time() - start < timeout:
            active = self.wm.get_active_window()
            if active and expected_partial_title.lower() in active.lower():
                return True
            
            # Also check if it exists at all, in case it didn't grab focus
            titles = self.wm.get_windows()
            if any(expected_partial_title.lower() in t.lower() for t in titles):
                return True
                
            time.sleep(0.5)
        
        logger.warning(f"Verification failed: expected '{expected_partial_title}' window to exist")
        return False

    def verify_window_closed(self, expected_partial_title: str, timeout: float = 2.0) -> bool:
        """Wait until no windows match the title."""
        start = time.time()
        while time.time() - start < timeout:
            titles = self.wm.get_windows()
            found = any(expected_partial_title.lower() in t.lower() for t in titles)
            if not found:
                return True
            time.sleep(0.5)
        
        logger.warning(f"Verification failed: expected '{expected_partial_title}' closed, but it remains visible.")
        return False
