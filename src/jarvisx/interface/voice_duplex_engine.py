"""Full-Duplex Voice Interaction Engine for Jarvis X.

Integrates real microphone STT (SpeechRecognition / PyAudio) and Windows SAPI / System.Speech TTS
with robust multi-threaded COM initialization and fallback execution.
"""

from __future__ import annotations
import os
import sys
import time
import threading
import subprocess
from typing import Optional, Callable

try:
    import speech_recognition as sr
    HAVE_SR = True
except Exception:
    HAVE_SR = False

try:
    import pythoncom
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
            self.recognizer.energy_threshold = 250
            self.recognizer.pause_threshold = 0.8
            self.recognizer.dynamic_energy_threshold = True

    def speak(self, text: str, sync: bool = False):
        """Speak out text aloud through laptop speakers and print cleanly."""
        if not text or not text.strip():
            return
        clean_text = text.strip()
        try:
            print(f"\n[JARVIS VOICE]: {clean_text}\n")
        except Exception:
            pass
        
        def _speak_thread():
            spoken = clean_text.replace("*", "").replace("#", "").replace("`", "").replace("[", "").replace("]", "").replace("\n", " ")
            
            # Method 1: Windows Native SAPI with COM Initialized
            if HAVE_SAPI:
                try:
                    pythoncom.CoInitialize()
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    speaker.Speak(spoken[:350])
                    pythoncom.CoUninitialize()
                    return
                except Exception:
                    pass

            # Method 2: PowerShell System.Speech Synthesizer (Zero-dependency Fallback)
            try:
                safe_spoken = spoken[:300].replace('"', ' ').replace("'", " ")
                cmd = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("{safe_spoken}")'
                subprocess.run(
                    ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", cmd],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
            except Exception:
                pass

        if sync:
            _speak_thread()
        else:
            threading.Thread(target=_speak_thread, daemon=True).start()

    def listen_and_transcribe(self) -> str:
        """Listens from live microphone, falling back to keyboard input if silent."""
        # 1. Try real live microphone audio listening
        if HAVE_SR and self.recognizer:
            try:
                with sr.Microphone() as source:
                    try:
                        print("\n[LISTENING] Speak into your mic (or press Enter to type)... ", end="", flush=True)
                    except Exception:
                        pass
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self.recognizer.listen(source, timeout=4.5, phrase_time_limit=12.0)
                    try:
                        print("\n[*] Transcribing audio...")
                    except Exception:
                        pass
                    text = self.recognizer.recognize_google(audio)
                    try:
                        print(f"You said: \"{text}\"")
                    except Exception:
                        pass
                    return text
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                pass
            except Exception:
                pass

        # 2. Interactive Terminal Fallback
        try:
            user_input = input("\n[TYPE PROMPT] You: ").strip()
            return user_input
        except (KeyboardInterrupt, EOFError):
            return "exit"


def get_voice_duplex_engine() -> VoiceDuplexEngine:
    return VoiceDuplexEngine()
