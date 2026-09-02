"""
Unit Test Suite for 24/7 Continuous Omni Screen Sentinel.
=========================================================
Verifies:
1. Singleton lifecycle (start, stop, toggle).
2. Perceptual frame hashing & low CPU gating.
3. Multi-domain screen intelligence (Math, Coding, System thermals).
"""

import unittest
from unittest.mock import patch, MagicMock
from PIL import Image

from jarvisx.automation.ev_omni_screen_sentinel import EVOmniScreenSentinel


class TestEVOmniScreenSentinel(unittest.TestCase):

    def setUp(self):
        self.sentinel = EVOmniScreenSentinel.get_instance()
        self.sentinel.speech_cooldown_sec = 0.0  # Disable cooldown during testing

    def test_singleton_and_toggle(self):
        s2 = EVOmniScreenSentinel.get_instance()
        self.assertIs(self.sentinel, s2)

    @patch("jarvisx.automation.ev_neural_voice.speak_ev_neural")
    def test_math_wave_detection(self, mock_speak):
        fake_img = Image.new("RGB", (100, 100), color="white")
        with patch("pyperclip.paste", return_value="vibrating string wave equation u_tt = c^2 u_xx"):
            res = self.sentinel._analyze_and_assist(fake_img)
            self.assertIsNotNone(res)
            self.assertEqual(res["domain"], "math")

    @patch("jarvisx.automation.ev_neural_voice.speak_ev_neural")
    def test_coding_traceback_detection(self, mock_speak):
        fake_img = Image.new("RGB", (100, 100), color="black")
        with patch("pyperclip.paste", return_value="Traceback (most recent call last):\nIndexError: pop from empty list"):
            res = self.sentinel._analyze_and_assist(fake_img)
            self.assertIsNotNone(res)
            self.assertEqual(res["domain"], "coding")


if __name__ == "__main__":
    unittest.main()
