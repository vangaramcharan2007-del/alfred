"""
Unit tests for ECurriculaDocEngine and GDriveHelper.
"""

import os
import sys
import unittest
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir / "src"))

from jarvisx.agents.ecurricula_doc_engine import ECurriculaDocEngine
from jarvisx.automation.gdrive_uploader import GDriveHelper


class TestECurriculaDocEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ECurriculaDocEngine(output_dir="outputs/test_srm")

    def test_create_crossword_assignment(self):
        data = {
            "across": ["4. STACK", "5. QUEUE"],
            "down": ["1. ARRAY", "2. TREE"]
        }
        res = self.engine.create_assignment(
            unit=2,
            session=1,
            slo=1,
            content_type="crossword",
            data=data
        )
        self.assertTrue(os.path.exists(res["docx_path"]))
        self.assertTrue(os.path.exists(res["pdf_path"]))
        self.assertGreater(os.path.getsize(res["pdf_path"]), 0)
        self.assertEqual(res["student"], "VANGA RAM CHARAN")
        self.assertEqual(res["reg_no"], "RA2511027010164")
        self.assertEqual(res["header"], "Unit 2, S1, SLO1")

    def test_create_matching_assignment(self):
        data = [
            {"no": "1", "left": "Stack", "code": "A", "text": "LIFO structure"},
            {"no": "2", "left": "Queue", "code": "B", "text": "FIFO structure"}
        ]
        res = self.engine.create_assignment(
            unit=2,
            session=1,
            slo=2,
            content_type="matching",
            data=data
        )
        self.assertTrue(os.path.exists(res["docx_path"]))
        self.assertTrue(os.path.exists(res["pdf_path"]))
        self.assertGreater(os.path.getsize(res["pdf_path"]), 0)

    def test_gdrive_link_validation(self):
        helper = GDriveHelper()
        valid_link = "https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q/view?usp=sharing"
        res = helper.validate_and_normalize_drive_link(valid_link)
        self.assertTrue(res["valid"])
        self.assertEqual(res["file_id"], "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q")

        invalid_link = "https://example.com/notadrive"
        res2 = helper.validate_and_normalize_drive_link(invalid_link)
        self.assertFalse(res2["valid"])


if __name__ == "__main__":
    unittest.main()
