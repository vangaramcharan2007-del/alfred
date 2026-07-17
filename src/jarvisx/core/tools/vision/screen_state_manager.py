import cv2
import numpy as np
from .vision_permissions import VisionPermissionManager, VisionTrustLevel

class ScreenStateManager:
    @staticmethod
    def get_screen_hash(image_path: str) -> str:
        VisionPermissionManager.require(VisionTrustLevel.SCREENSHOT_ONLY)
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Image {image_path} not found")
        # simple average hash
        resized = cv2.resize(img, (8, 8))
        mean_val = np.mean(resized)
        hash_bits = (resized > mean_val).flatten().astype(int)
        return "".join(map(str, hash_bits))
        
    @staticmethod
    def detect_change(img_path1: str, img_path2: str, threshold: float = 0.95) -> bool:
        """Returns True if screens are structurally different (similarity < threshold)."""
        VisionPermissionManager.require(VisionTrustLevel.SCREENSHOT_ONLY)
        img1 = cv2.imread(img_path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(img_path2, cv2.IMREAD_GRAYSCALE)
        if img1 is None or img2 is None:
            return True
            
        if img1.shape != img2.shape:
            return True
            
        diff = cv2.absdiff(img1, img2)
        non_zero_count = np.count_nonzero(diff > 30) # small threshold for noise
        total_pixels = img1.shape[0] * img1.shape[1]
        similarity = 1.0 - (non_zero_count / total_pixels)
        
        return similarity < threshold
