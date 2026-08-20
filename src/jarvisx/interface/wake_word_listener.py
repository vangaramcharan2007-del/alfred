"""Jarvis X: 24/7 Background Wake-Word Detection Engine.

Listens continuously for hotwords ("hey jarvis", "jarvis", "nani") using
ambient energy thresholding and triggers autonomous voice callbacks.
"""

from __future__ import annotations
import os
import sys
import time
import threading
from typing import Callable, Optional

try:
    import speech_recognition as sr
    HAVE_SR = True
except Exception:
    HAVE_SR = False


class WakeWordListener:
    """Continuous low-CPU wake-word listener for 'Hey Jarvis'."""

    WAKE_WORDS = ["hey jarvis", "jarvis", "nani", "alfred", "wake up"]

    def __init__(self, on_wake_callback: Optional[Callable[[], None]] = None):
        self.callback = on_wake_callback
        self.is_running = False
        self.recognizer = sr.Recognizer() if HAVE_SR else None
        if self.recognizer:
            self.recognizer.energy_threshold = 280
            self.recognizer.pause_threshold = 0.6
            self.recognizer.dynamic_energy_threshold = True

    def check_phrase_for_wakeword(self, phrase: str) -> bool:
        """Returns True if the transcribed phrase contains any registered wake word."""
        clean = phrase.lower().strip()
        return any(w in clean for w in self.WAKE_WORDS)

    def start_listening_thread(self, callback: Optional[Callable[[], None]] = None):
        """Starts the background listening loop in a daemon thread."""
        if callback:
            self.callback = callback
        self.is_running = True
        t = threading.Thread(target=self._listen_loop, daemon=True)
        t.start()
        return t

    def _listen_loop(self):
        """Internal audio monitoring loop."""
        if not HAVE_SR or not self.recognizer:
            print("[WAKE_WORD] SpeechRecognition unavailable.")
            return

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                while self.is_running:
                    try:
                        audio = self.recognizer.listen(source, timeout=3.0, phrase_time_limit=3.0)
                        text = self.recognizer.recognize_google(audio).lower()
                        if self.check_phrase_for_wakeword(text):
                            print(f"\n[WAKE_WORD] >>> Hotword Detected: '{text}' <<<")
                            if self.callback:
                                self.callback()
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        continue
                    except Exception:
                        time.sleep(0.5)
        except Exception as e:
            print(f"[WAKE_WORD] Microphone listener error: {e}")

    def stop(self):
        self.is_running = False
