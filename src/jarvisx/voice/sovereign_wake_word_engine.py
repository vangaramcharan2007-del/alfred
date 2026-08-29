"""
Sovereign Wake-Word & Hands-Free Audio Engine for Alfred OS.
Directly interfaces with laptop hardware microphone via sounddevice (Zero-PyAudio requirement),
uses adaptive RMS energy gate, and transcribes speech to trigger autonomous LLM missions.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import time
from typing import Callable, List, Optional

import numpy as np
import sounddevice as sd
import speech_recognition as sr

logger = logging.getLogger("jarvisx.voice.wakeword")


class SovereignWakeWordEngine:
    """Continuous hands-free wake-word detector & voice listener using sounddevice."""

    WAKE_WORDS = [
        "hey alfred", "alfred", "jarvis", "hey jarvis", "nani", "friday", "edith", "wake up"
    ]

    def __init__(
        self,
        sample_rate: int = 16000,
        energy_threshold: float = 120.0,
        on_command_callback: Optional[Callable[[str], None]] = None
    ):
        self.sample_rate = sample_rate
        self.energy_threshold = energy_threshold
        self.callback = on_command_callback
        self.is_listening = False
        self._thread: Optional[threading.Thread] = None
        self.recognizer = sr.Recognizer()

    def is_wake_phrase(self, text: str) -> bool:
        clean = text.lower().strip()
        return any(w in clean for w in self.WAKE_WORDS)

    def extract_command(self, text: str) -> str:
        """Strips the wake word prefix and returns the clean command."""
        clean = text.strip()
        lower = clean.lower()
        for w in sorted(self.WAKE_WORDS, key=len, reverse=True):
            if lower.startswith(w):
                cmd = clean[len(w):].strip(" ,:.-")
                if cmd:
                    return cmd
        return clean

    def start_listening(self, callback: Optional[Callable[[str], None]] = None):
        """Starts background continuous microphone listening."""
        if callback:
            self.callback = callback
        if self.is_listening:
            return
        self.is_listening = True
        self._thread = threading.Thread(
            target=self._continuous_mic_loop,
            daemon=True,
            name="SovereignWakeWordThread"
        )
        self._thread.start()
        logger.info("Sovereign Wake-Word Engine active on microphone.")

    def stop_listening(self):
        self.is_listening = False

    def _continuous_mic_loop(self):
        chunk_duration = 0.5  # 500ms audio chunks
        chunk_samples = int(chunk_duration * self.sample_rate)

        while self.is_listening:
            try:
                # 1. Listen for voice energy burst
                rec_block = sd.rec(chunk_samples, samplerate=self.sample_rate, channels=1, dtype="int16")
                sd.wait()
                energy = float(np.abs(rec_block).mean())

                if energy > self.energy_threshold:
                    # Voice detected! Record 3.5 seconds of user speech
                    speech_duration = 3.5
                    speech_samples = int(speech_duration * self.sample_rate)
                    print(f"\n[MIC] 🎙️ Voice detected (Energy: {energy:.1f}) — Recording phrase...")
                    
                    full_audio = sd.rec(speech_samples, samplerate=self.sample_rate, channels=1, dtype="int16")
                    sd.wait()

                    # Transcribe using speech_recognition + Google STT
                    raw_bytes = full_audio.tobytes()
                    audio_data = sr.AudioData(raw_bytes, self.sample_rate, 2)

                    try:
                        transcription = self.recognizer.recognize_google(audio_data).strip()
                        print(f"[MIC] 🗣️ Heard: \"{transcription}\"")

                        # Check if wake word or direct command
                        if self.is_wake_phrase(transcription):
                            cmd = self.extract_command(transcription)
                            print(f"[WAKE WORD] ⚡ WAKE WORD ACTIVATED! Clean Command: \"{cmd}\"")
                            if self.callback:
                                self.callback(cmd or "hello")
                        elif self.callback:
                            # Also allow direct commands
                            self.callback(transcription)

                    except sr.UnknownValueError:
                        # Inaudible audio/background click
                        pass
                    except Exception as e:
                        logger.warning(f"STT error: {e}")

            except Exception as ex:
                logger.error(f"Mic loop error: {ex}")
                time.sleep(0.5)


def get_wakeword_engine(callback: Optional[Callable[[str], None]] = None) -> SovereignWakeWordEngine:
    return SovereignWakeWordEngine(on_command_callback=callback)
