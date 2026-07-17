from mss import mss
import os
from .desktop_permissions import DesktopPermissionManager, DesktopTrustLevel
from .logger import DesktopLogger

class ScreenshotManager:
    @staticmethod
    def capture_fullscreen(output_path: str = "screenshot.png") -> str:
        DesktopPermissionManager.require(DesktopTrustLevel.READ_ONLY)
        DesktopLogger.log_action("ScreenshotManager", "CAPTURE", f"Capturing full screen to {output_path}")
        
        with mss() as sct:
            filename = sct.shot(output=output_path)
            
        # State verification
        if not os.path.exists(filename):
            DesktopLogger.log_error("ScreenshotManager", "CAPTURE_VERIFY", f"Screenshot {filename} not created")
            raise RuntimeError(f"Screenshot file {filename} does not exist after capture")
            
        DesktopLogger.log_action("ScreenshotManager", "CAPTURE_VERIFY", "Screenshot saved successfully")
        return filename
