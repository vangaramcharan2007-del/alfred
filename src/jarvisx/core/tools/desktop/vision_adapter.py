from .desktop_permissions import DesktopPermissionManager, DesktopTrustLevel

class VisionAdapter:
    """
    Interface for future OCR and vision processing integrations.
    """
    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        DesktopPermissionManager.require(DesktopTrustLevel.READ_ONLY)
        # Placeholder for pytesseract / paddleocr integration
        raise NotImplementedError("Vision capabilities are planned for a future phase.")
        
    @staticmethod
    def locate_element_on_screen(template_path: str) -> tuple[int, int]:
        DesktopPermissionManager.require(DesktopTrustLevel.READ_ONLY)
        # Placeholder for cv2 template matching
        raise NotImplementedError("Vision capabilities are planned for a future phase.")
