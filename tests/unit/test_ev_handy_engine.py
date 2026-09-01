"""
Unit Test Suite for E-V Handy Voice Dictation Engine.
====================================================
"""

import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from jarvisx.voice.ev_handy_engine import EVHandyVoiceDictationEngine


class TestEVHandyVoiceDictationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = EVHandyVoiceDictationEngine.get_instance()

    def test_singleton_instance(self):
        engine2 = EVHandyVoiceDictationEngine.get_instance()
        self.assertIs(self.engine, engine2)

    @patch("pyperclip.copy")
    @patch("pyautogui.hotkey")
    def test_type_text_into_active_window(self, mock_hotkey, mock_copy):
        test_text = "Testing Handy direct OS dictation"
        self.engine.type_text_into_active_window(test_text)
        mock_copy.assert_called_once_with(test_text)
        mock_hotkey.assert_called_once_with('ctrl', 'v')

    @patch("sounddevice.InputStream")
    def test_start_and_stop_recording_lifecycle(self, mock_stream):
        self.engine.start_recording()
        self.assertTrue(self.engine.is_recording)
        
        # Inject dummy audio frames
        dummy_frame = np.zeros((100, 1), dtype=np.int16)
        self.engine.audio_frames.append(dummy_frame)
        
        with patch.object(self.engine.recognizer, "recognize_google", return_value="hello alfred"):
            text = self.engine.stop_and_transcribe()
            self.assertEqual(text, "hello alfred")
            self.assertFalse(self.engine.is_recording)


if __name__ == "__main__":
    unittest.main()
