import os
import time
from typing import List, Dict, Any, Optional
from .ui_map import UIMap
from .vision_permissions import VisionPermissionManager, VisionTrustLevel

class VisionMemory:
    def __init__(self, storage_dir: str = "var/vision_memory"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.history: List[UIMap] = []
        self.fingerprints: Dict[str, Any] = {}

    def store_ui_map(self, ui_map: UIMap):
        VisionPermissionManager.require(VisionTrustLevel.SCREENSHOT_ONLY)
        self.history.append(ui_map)

    def get_latest(self) -> Optional[UIMap]:
        return self.history[-1] if self.history else None
