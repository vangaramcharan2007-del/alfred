import pytesseract
from PIL import Image
import cv2
import os
from typing import List, Dict, Any
from .ui_map import UIElement, UIBoundingBox
from .vision_permissions import VisionPermissionManager, VisionTrustLevel

# Configure tesseract path for Windows
tesseract_paths = [
    r"C:\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
]
for p in tesseract_paths:
    if os.path.exists(p):
        pytesseract.pytesseract.tesseract_cmd = p
        break

class OCREngine:
    @staticmethod
    def extract_text(image_path: str) -> str:
        VisionPermissionManager.require(VisionTrustLevel.OCR_READ)
        img = Image.open(image_path)
        return pytesseract.image_to_string(img)
        
    @staticmethod
    def extract_elements(image_path: str) -> List[UIElement]:
        VisionPermissionManager.require(VisionTrustLevel.OCR_READ)
        img = cv2.imread(image_path)
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        elements = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if text:
                conf = float(data['conf'][i]) / 100.0
                bbox = UIBoundingBox(
                    x=data['left'][i],
                    y=data['top'][i],
                    width=data['width'][i],
                    height=data['height'][i]
                )
                elements.append(UIElement(
                    id=f"text_{i}",
                    type="text",
                    bbox=bbox,
                    text=text,
                    confidence=conf
                ))
        return elements
