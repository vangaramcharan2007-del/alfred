import pytest
import os
import cv2
import numpy as np
from jarvisx.core.tools.vision import (
    VisionPermissionManager, VisionTrustLevel, 
    ScreenStateManager, UIDetector
)

def setup_module():
    VisionPermissionManager.set_level(VisionTrustLevel.FULL_VISION)
    os.makedirs("var", exist_ok=True)
    
    # Create dummy images for testing
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(img1, (10, 10), (50, 50), (255, 255, 255), -1)
    cv2.imwrite("var/test_img1.png", img1)
    
    img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    cv2.imwrite("var/test_img2.png", img2)

def test_screen_hash():
    hash1 = ScreenStateManager.get_screen_hash("var/test_img1.png")
    assert isinstance(hash1, str)
    assert len(hash1) == 64

def test_screen_change_detection():
    # Should detect change between the two different images
    changed = ScreenStateManager.detect_change("var/test_img1.png", "var/test_img2.png")
    assert changed == True
    
    # Same image should not trigger change
    changed = ScreenStateManager.detect_change("var/test_img1.png", "var/test_img1.png")
    assert changed == False

def test_ui_detector():
    regions = UIDetector.detect_regions("var/test_img1.png")
    assert len(regions) > 0
