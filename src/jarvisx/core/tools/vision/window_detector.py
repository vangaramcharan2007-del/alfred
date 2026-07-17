import cv2
from typing import List
from .ui_map import UIElement, UIBoundingBox
from .vision_permissions import VisionPermissionManager, VisionTrustLevel

class WindowDetector:
    @staticmethod
    def detect_windows(image_path: str) -> List[UIElement]:
        VisionPermissionManager.require(VisionTrustLevel.FULL_VISION)
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Thresholding to find large window blocks
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        elements = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            # Filter for window-sized components
            if w > 200 and h > 150:
                elements.append(UIElement(
                    id=f"window_{i}",
                    type="window",
                    bbox=UIBoundingBox(x, y, w, h),
                    confidence=1.0
                ))
                
        return elements
