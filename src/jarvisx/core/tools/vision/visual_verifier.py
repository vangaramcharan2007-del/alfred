from typing import List
from .ocr_engine import OCREngine
from .ui_map import UIElement
from .vision_permissions import VisionPermissionManager, VisionTrustLevel

class VisualVerifier:
    @staticmethod
    def verify_text_present(image_path: str, expected_text: str, min_confidence: float = 0.5) -> bool:
        VisionPermissionManager.require(VisionTrustLevel.OCR_READ)
        elements = OCREngine.extract_elements(image_path)
        expected_lower = expected_text.lower()
        
        for el in elements:
            if el.text and el.confidence >= min_confidence:
                if expected_lower in el.text.lower():
                    return True
        return False
        
    @staticmethod
    def verify_ui_change(img_path1: str, img_path2: str, threshold: float = 0.95) -> bool:
        from .screen_state_manager import ScreenStateManager
        return ScreenStateManager.detect_change(img_path1, img_path2, threshold)
