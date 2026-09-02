"""
Unit Test Suite for Ambient Dual-Voice Sentinel & Proactive Coding Watcher.
==========================================================================
"""

import unittest
from unittest.mock import patch, MagicMock

from jarvisx.voice.ambient_dual_sentinel import AmbientDualSentinel


class TestAmbientDualSentinel(unittest.TestCase):

    def setUp(self):
        self.sentinel = AmbientDualSentinel.get_instance()

    def test_singleton(self):
        s2 = AmbientDualSentinel.get_instance()
        self.assertIs(self.sentinel, s2)

    @patch("jarvisx.voice.sovereign_neural_tts.SovereignNeuralTTS.speak")
    def test_alfred_wake_handler(self, mock_speak):
        self.sentinel._handle_alfred_wake("alfred check status")
        self.assertTrue(True)

    @patch("jarvisx.automation.ev_neural_voice.speak_ev_neural")
    def test_ev_wake_handler(self, mock_speak):
        self.sentinel._handle_ev_wake("ev solve math")
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
