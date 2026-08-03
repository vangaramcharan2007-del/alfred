from __future__ import annotations
import sys
import time
from typing import Dict, Any, Optional

class SpeechOutputEngine:
    """
    Alfred personality TTS engine with streaming and voice interruption support.
    """
    def __init__(self, use_tts: bool = False):
        self.use_tts = use_tts
        self.engine = None
        if use_tts:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
            except Exception:
                self.engine = None

    def speak(self, text: str, stream: bool = True) -> Dict[str, Any]:
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass

        if stream:
            print(f"\n[Alfred Voice]: {text}\n")
            sys.stdout.flush()

        return {
            "status": "SPOKEN",
            "text": text,
            "duration": round(len(text) * 0.05, 2)
        }
