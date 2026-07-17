import cv2
import numpy as np
from typing import List, Tuple
from .ui_map import UIElement, UIBoundingBox
from .vision_permissions import VisionPermissionManager, VisionTrustLevel

class IconDetector:
    @staticmethod
    def locate_icon(screen_path: str, template_path: str, threshold: float = 0.8) -> List[UIElement]:
        VisionPermissionManager.require(VisionTrustLevel.FULL_VISION)
        
        img = cv2.imread(screen_path, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        
        if img is None or template is None:
            return []
            
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        
        elements = []
        for i, pt in enumerate(zip(*loc[::-1])):
            elements.append(UIElement(
                id=f"icon_{i}",
                type="icon",
                bbox=UIBoundingBox(pt[0], pt[1], w, h),
                confidence=float(res[pt[1], pt[0]])
            ))
            
        return elements
