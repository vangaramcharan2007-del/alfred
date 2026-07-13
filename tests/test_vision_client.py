import unittest
from unittest.mock import patch, MagicMock
from jarvisx.clients.tesseract_client import TesseractClient

class TestVisionClient(unittest.TestCase):

    @patch("jarvisx.clients.tesseract_client.HAVE_TESSERACT", False)
    def test_tesseract_disabled(self):
        client = TesseractClient()
        result = client.extract_text(b"fake_image_data")
        self.assertIn("OCR is currently disabled", result)

    @patch("jarvisx.clients.tesseract_client.HAVE_TESSERACT", True)
    @patch("jarvisx.clients.tesseract_client.Image.open")
    @patch("jarvisx.clients.tesseract_client.pytesseract.image_to_string")
    def test_tesseract_success(self, mock_image_to_string, mock_image_open):
        mock_image_to_string.return_value = "Hello World\n\n"
        client = TesseractClient()
        result = client.extract_text(b"fake_image_data")
        self.assertEqual(result, "Hello World")
        mock_image_open.assert_called_once()
        mock_image_to_string.assert_called_once()

    @patch("jarvisx.clients.tesseract_client.HAVE_TESSERACT", True)
    @patch("jarvisx.clients.tesseract_client.Image.open")
    def test_tesseract_failure(self, mock_image_open):
        mock_image_open.side_effect = Exception("Cannot open image")
        client = TesseractClient()
        result = client.extract_text(b"fake_image_data")
        self.assertTrue(result.startswith("Failed to extract text"))

if __name__ == "__main__":
    unittest.main()
