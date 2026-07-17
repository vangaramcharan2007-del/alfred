import cv2
import numpy as np
from typing import List
from .ui_map import UIElement, UIBoundingBox
from .vision_permissions import VisionPermissionManager, VisionTrustLevel

class UIDetector:
    @staticmethod
    def detect_regions(image_path: str) -> List[UIElement]:
        VisionPermissionManager.require(VisionTrustLevel.FULL_VISION)
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Edge detection to find UI boundaries
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        elements = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            if w > 10 and h > 10 and w < img.shape[1] * 0.9 and h < img.shape[0] * 0.9:
                elements.append(UIElement(
                    id=f"region_{i}",
                    type="region",
                    bbox=UIBoundingBox(x, y, w, h),
                    confidence=1.0
                ))
                
        return elements
