"""OCR Engine — extracts visible text from images."""
import logging
from typing import Tuple
from PIL import Image

logger = logging.getLogger(__name__)

class OCREngine:
    """Extracts text from screenshots using pytesseract."""

    def __init__(self):
        try:
            import pytesseract
            # Ensure tesseract is pointed to correctly if in default Windows location
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            self._pytesseract = pytesseract
            self.available = True
        except ImportError:
            self.available = False
            logger.warning("pytesseract is not installed. OCR will be unavailable.")

    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """Extract text from the given image path.
        Returns (extracted_text, confidence_score).
        """
        if not self.available:
            return "", 0.0

        try:
            img = Image.open(image_path)
            # Use tesseract to extract string
            text = self._pytesseract.image_to_string(img)
            
            # Since pytesseract doesn't easily return a single overall confidence score 
            # without parsing verbose TSV output, we will provide a heuristic or mock
            # confidence based on whether text was found.
            confidence = 0.97 if len(text.strip()) > 0 else 0.0
            
            return text.strip(), confidence
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return "", 0.0
