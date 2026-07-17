"""Screen Capture Service — captures desktop screenshots for visual analysis."""
import os
import time
import mss
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class ScreenCapture:
    """Handles full and partial desktop screenshots."""

    def __init__(self, save_dir: str = "var/screenshots"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def capture_full_screen(self) -> str:
        """Capture the primary monitor and save it to disk. Returns filepath."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.save_dir, f"screen_{timestamp}.png")
        
        try:
            with mss.mss() as sct:
                # monitor 1 is usually the primary monitor
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=filepath)
                
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return ""
