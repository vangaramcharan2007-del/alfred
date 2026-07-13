import io
import logging
from typing import Optional

try:
    from PIL import Image
    import pytesseract
    HAVE_TESSERACT = True
except ImportError:
    HAVE_TESSERACT = False

logger = logging.getLogger(__name__)


class TesseractClient:
    """Client for extracting text from images using Tesseract OCR."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        if not HAVE_TESSERACT:
            logger.warning("pytesseract or Pillow is not installed. OCR will not work.")
        
        if tesseract_cmd and HAVE_TESSERACT:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image_data: bytes) -> str:
        """Extract text from raw image bytes."""
        if not HAVE_TESSERACT:
            return "OCR is currently disabled because pytesseract or Pillow is not installed."
            
        try:
            image = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return f"Failed to extract text from image: {e}"
