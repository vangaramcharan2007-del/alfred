from mss import mss
import os
import time
from typing import Optional
from .vision_permissions import VisionPermissionManager, VisionTrustLevel

class ScreenCapture:
    @staticmethod
    def capture(output_path: Optional[str] = None) -> str:
        VisionPermissionManager.require(VisionTrustLevel.SCREENSHOT_ONLY)
        if not output_path:
            os.makedirs("var/screenshots", exist_ok=True)
            output_path = f"var/screenshots/screen_{int(time.time()*1000)}.png"
            
        with mss() as sct:
            filename = sct.shot(output=output_path)
            
        return filename
