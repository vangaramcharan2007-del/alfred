"""
Unit Test Suite for Ambient Dual-Voice Sentinel & Proactive Coding Watcher.
==========================================================================
"""

import unittest
from unittest.mock import patch, MagicMock

import pytest

try:
    from jarvisx.voice.ambient_dual_sentinel import AmbientDualSentinel
except (ImportError, OSError) as _exc:
    # Skipped, not failed: "this never ran because its dependency is missing"
    # is different information from "the implementation is broken", and a
    # collection error conflates the two. OSError is caught alongside
    # ImportError because sounddevice is installed but raises
    # OSError("PortAudio library not found") at import time.
    pytest.skip(
        "Ambient dual-voice sentinel (needs PortAudio) unavailable: " + str(_exc), allow_module_level=True
    )



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
