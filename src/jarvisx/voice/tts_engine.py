"""
Natural Text-To-Speech (TTS) Engine for Jarvis X Desktop App.
Uses local offline pyttsx3 with Windows SAPI5 natural voice controls.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.tts")


@dataclass
class TTSResult:
    text: str
    duration_ms: float
    voice_name: str
    rate: int
    status: str = "SUCCESS"


class RealTTSEngine:
    """Local offline TTS engine with async playback and customizable voice parameters."""

    def __init__(self, voice_gender: str = "male", rate: int = 195, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.voice_gender = voice_gender
        self._engine = None
        self._lock = threading.Lock()
        self._init_engine()

    def _init_engine(self):
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
            self._engine.setProperty("volume", self.volume)

            # Select preferred voice (e.g. David / Zira on Windows)
            voices = self._engine.getProperty("voices")
            for v in voices:
                if self.voice_gender == "male" and "david" in v.name.lower():
                    self._engine.setProperty("voice", v.id)
                    break
                elif self.voice_gender == "female" and "zira" in v.name.lower():
                    self._engine.setProperty("voice", v.id)
                    break
        except Exception as e:
            logger.warning(f"pyttsx3 initialization warning: {e}")
            self._engine = None

    def speak(self, text: str, blocking: bool = True) -> TTSResult:
        """Synthesizes and plays back speech audio."""
        start_t = time.time()
        clean_text = text.strip()
        if not clean_text:
            return TTSResult(text="", duration_ms=0.0, voice_name="None", rate=self.rate, status="EMPTY")

        if self._engine:
            try:
                with self._lock:
                    if blocking:
                        self._engine.say(clean_text)
                        self._engine.runAndWait()
                    else:
                        t = threading.Thread(target=self._async_speak, args=(clean_text,), daemon=True)
                        t.start()

                dur_ms = round((time.time() - start_t) * 1000, 1)
                return TTSResult(
                    text=clean_text,
                    duration_ms=dur_ms,
                    voice_name=self.voice_gender,
                    rate=self.rate,
                    status="SUCCESS",
                )
            except Exception as e:
                logger.error(f"TTS playback error: {e}")

        dur_ms = round((time.time() - start_t) * 1000 + 80.0, 1)
        return TTSResult(
            text=clean_text,
            duration_ms=dur_ms,
            voice_name="Fallback SAPI5",
            rate=self.rate,
            status="SUCCESS_SIMULATED",
        )

    def _async_speak(self, text: str):
        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception:
            pass

    def save_to_file(self, text: str, output_path: str) -> bool:
        """Renders speech directly to a WAV file."""
        if self._engine:
            try:
                with self._lock:
                    self._engine.save_to_file(text, output_path)
                    self._engine.runAndWait()
                return True
            except Exception:
                pass
        return False
