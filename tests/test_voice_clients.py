import json
import unittest
from unittest.mock import MagicMock

from jarvisx.adapters.voice_interface import STTProvider, TTSProvider
from jarvisx.clients.elevenlabs_client import ElevenLabsClient
from jarvisx.clients.openai_client import OpenAIClient


class TestVoiceProviders(unittest.TestCase):

    def test_stt_fallback(self) -> None:
        # Client not configured, should fallback
        client = OpenAIClient(api_key="")
        stt = STTProvider(client=client)
        
        # Test fallback parsing JSON
        result = stt.transcribe(json.dumps({"text": "hello"}).encode("utf-8"))
        self.assertEqual(result, "hello")
        
        # Test fallback raw audio failure (default text)
        result = stt.transcribe(b"random_audio_bytes")
        self.assertEqual(result, "Simulated voice input text")

    def test_stt_configured(self) -> None:
        # Mock client behavior
        client = OpenAIClient(api_key="fake")
        client.transcribe = MagicMock(return_value="actual transcription")
        
        stt = STTProvider(client=client)
        result = stt.transcribe(b"audio")
        self.assertEqual(result, "actual transcription")
        client.transcribe.assert_called_with(b"audio")

    def test_tts_fallback(self) -> None:
        client = ElevenLabsClient(api_key="")
        tts = TTSProvider(client=client)
        
        result_bytes = tts.synthesize("hello", "edith", {})
        result = json.loads(result_bytes.decode("utf-8"))
        
        self.assertEqual(result["text"], "hello")
        self.assertEqual(result["voice_profile"], "edith")
        self.assertEqual(result["status"], "synthesized")

    def test_tts_configured(self) -> None:
        client = ElevenLabsClient(api_key="fake")
        client.synthesize = MagicMock(return_value=b"audio_out")
        
        tts = TTSProvider(client=client)
        result = tts.synthesize("hello", "alfred", {})
        
        self.assertEqual(result, b"audio_out")
        client.synthesize.assert_called_with("hello", voice_id=ElevenLabsClient.VOICE_ALFRED)


if __name__ == "__main__":
    unittest.main()
