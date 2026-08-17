"""Full-Duplex Voice Interaction Engine for Jarvis X.

Integrates real microphone STT (SpeechRecognition / Whisper) and Windows SAPI TTS
with hands-free live audio listening and terminal input fallback.
"""

from __future__ import annotations
import os
import sys
import time
import threading
from typing import Optional, Callable

try:
    import speech_recognition as sr
    HAVE_SR = True
except Exception:
    HAVE_SR = False

try:
    import win32com.client
    HAVE_SAPI = True
except Exception:
    HAVE_SAPI = False


class VoiceDuplexEngine:
    """Voice Engine providing real speech-to-text listening and text-to-speech feedback."""

    def __init__(
        self,
        whisper_model_path: str = "./models/ggml-base.en.bin",
        piper_model_path: str = "./models/en_US-lessac-medium.onnx"
    ):
        self.whisper_path = whisper_model_path
        self.piper_path = piper_model_path
        self.is_listening = False
        self.recognizer = sr.Recognizer() if HAVE_SR else None
        if self.recognizer:
            self.recognizer.energy_threshold = 300
            self.recognizer.pause_threshold = 0.8
            self.recognizer.dynamic_energy_threshold = True

    def speak(self, text: str):
        """Speak out text aloud through laptop speakers and print cleanly."""
        if not text or not text.strip():
            return
        clean_text = text.strip()
        print(f"\n🗣️  [JARVIS VOICE]: {clean_text}\n")
        
        def _speak_thread():
            try:
                if HAVE_SAPI:
                    # Windows Native SAPI 5.4 Voice Synthesizer
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    # Clean markdown formatting symbols before speaking
                    spoken = clean_text.replace("*", "").replace("#", "").replace("`", "").replace("[", "").replace("]", "")
                    speaker.Speak(spoken[:300])
            except Exception:
                pass

        # Speak asynchronously so audio doesn't block the core
        threading.Thread(target=_speak_thread, daemon=True).start()

    def listen_and_transcribe(self) -> str:
        """Listens from live microphone, falling back to keyboard input if silent."""
        # 1. Try real live microphone audio listening
        if HAVE_SR and self.recognizer:
            try:
                with sr.Microphone() as source:
                    print("\n🎙️ [LISTENING] (Speak into your mic or press Enter to type)...", end="", flush=True)
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    audio = self.recognizer.listen(source, timeout=3.5, phrase_time_limit=10.0)
                    print("\n[*] Transcribing audio...")
                    text = self.recognizer.recognize_google(audio)
                    print(f"👉 You said: \"{text}\"")
                    return text
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                pass
            except Exception:
                pass

        # 2. Interactive Terminal Fallback
        try:
            user_input = input("\n💬 [TYPE PROMPT] You: ").strip()
            return user_input
        except (KeyboardInterrupt, EOFError):
            return "exit"


def get_voice_duplex_engine() -> VoiceDuplexEngine:
    return VoiceDuplexEngine()
