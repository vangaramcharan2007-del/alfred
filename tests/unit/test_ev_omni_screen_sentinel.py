"""
Unit Test Suite for Actuating Omni Screen Sentinel & Minimal Speech.
====================================================================
"""

import unittest
from unittest.mock import patch, MagicMock
from PIL import Image

from jarvisx.automation.ev_omni_screen_sentinel import EVOmniScreenSentinel, speak_minimal


class TestActuatingOmniSentinel(unittest.TestCase):

    def setUp(self):
        self.sentinel = EVOmniScreenSentinel.get_instance()
        self.sentinel.speech_cooldown_sec = 0.0

    @patch("jarvisx.automation.ev_omni_screen_sentinel.speak_ev_neural")
    def test_speak_minimal_strips_chatter(self, mock_speak):
        speak_minimal("Hello boss! I noticed that there is an IndexError on your screen. Let me fix it.")
        mock_speak.assert_called()
        spoken = mock_speak.call_args[0][0]
        # Must be concise (<= 6 words)
        self.assertTrue(len(spoken.split()) <= 6)

    @patch("jarvisx.automation.ev_omni_screen_sentinel.speak_minimal")
    def test_actuation_code_patch_to_clipboard(self, mock_speak):
        fake_img = Image.new("RGB", (100, 100), color="black")
        with patch("pyperclip.paste", return_value="Traceback (most recent call last):\nIndexError: list index out of range"):
            with patch("pyperclip.copy") as mock_copy:
                res = self.sentinel._analyze_and_actuate(fake_img)
                self.assertIsNotNone(res)
                self.assertEqual(res["action"], "code_patched")
                mock_copy.assert_called()

    @patch("jarvisx.automation.ev_omni_screen_sentinel.speak_minimal")
    def test_actuation_math_derivation(self, mock_speak):
        fake_img = Image.new("RGB", (100, 100), color="white")
        with patch("pyperclip.paste", return_value="solve 1D heat equation u_t = alpha^2 u_xx"):
            with patch("jarvisx.automation.ev_whatsapp_direct_click_sender.direct_send"):
                res = self.sentinel._analyze_and_actuate(fake_img)
                self.assertIsNotNone(res)
                self.assertEqual(res["action"], "math_derived")


if __name__ == "__main__":
    unittest.main()
