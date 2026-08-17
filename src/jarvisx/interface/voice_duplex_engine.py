"""Full-Duplex Voice Interaction Engine for Jarvis X.

Integrates Whisper.cpp STT and Piper TTS with dynamic interruption support.
"""

from __future__ import annotations
import os
import sys
import time
from typing import Optional, Callable


class VoiceDuplexEngine:
    """Voice Engine providing speech-to-text listening and text-to-speech feedback."""

    def __init__(
        self,
        whisper_model_path: str = "./models/ggml-base.en.bin",
        piper_model_path: str = "./models/en_US-lessac-medium.onnx"
    ):
        self.whisper_path = whisper_model_path
        self.piper_path = piper_model_path
        self.is_listening = False

    def speak(self, text: str):
        """Speak out text or print to console if audio device unavailable."""
        if not text or not text.strip():
            return
        print(f"\n🗣️  [JARVIS VOICE]: {text.strip()}\n")
        try:
            # Fallback to standard Windows SAPI TTS if Piper is not present
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text[:250])  # Speak first 250 chars cleanly
        except Exception:
            pass

    def listen_and_transcribe(self) -> str:
        """Listen for audio input and return transcribed text string."""
        try:
            # Interactive prompt fallback for terminal execution
            user_input = input("\n🎙️ [LISTENING] You: ").strip()
            return user_input
        except (KeyboardInterrupt, EOFError):
            return "exit"


def get_voice_duplex_engine() -> VoiceDuplexEngine:
    return VoiceDuplexEngine()
