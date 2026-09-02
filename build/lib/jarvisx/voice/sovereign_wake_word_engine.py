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
        energy_threshold: float = 45.0,
        on_command_callback: Optional[Callable[[str], None]] = None
    ):
        self.sample_rate = sample_rate
        self.energy_threshold = energy_threshold
        self.ambient_baseline = 35.0
        self.callback = on_command_callback
        self.is_listening = False
        self.is_speaking_tts = False
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

    def record_and_transcribe_manual(self, duration_sec: float = 4.0) -> Optional[str]:
        """Manually records a voice phrase and returns transcription (Push-to-Talk)."""
        print(f"\n[MIC] 🎙️ Recording voice phrase for {duration_sec}s...")
        samples = int(duration_sec * self.sample_rate)
        audio = sd.rec(samples, samplerate=self.sample_rate, channels=1, dtype="int16")
        sd.wait()
        
        raw_bytes = audio.tobytes()
        audio_data = sr.AudioData(raw_bytes, self.sample_rate, 2)
        try:
            text = self.recognizer.recognize_google(audio_data).strip()
            print(f"[MIC] 🗣️ Heard: \"{text}\"")
            if self.callback:
                clean_cmd = self.extract_command(text)
                self.callback(clean_cmd or text)
            return text
        except Exception as e:
            print(f"[MIC] STT Note: {e}")
            return None

    def _continuous_mic_loop(self):
        chunk_duration = 0.4  # 400ms audio chunks
        chunk_samples = int(chunk_duration * self.sample_rate)

        while self.is_listening:
            if self.is_speaking_tts:
                time.sleep(0.3)
                continue

            try:
                # 1. Sample ambient chunk
                rec_block = sd.rec(chunk_samples, samplerate=self.sample_rate, channels=1, dtype="int16")
                sd.wait()
                energy = float(np.abs(rec_block).mean())

                # Update adaptive noise floor
                self.ambient_baseline = 0.92 * self.ambient_baseline + 0.08 * energy
                dynamic_threshold = max(self.energy_threshold, self.ambient_baseline * 1.6)

                if energy > dynamic_threshold:
                    # Voice burst detected! Record 3.5 seconds
                    speech_duration = 3.5
                    speech_samples = int(speech_duration * self.sample_rate)
                    print(f"\n[MIC] 🎙️ Voice detected (Volume: {energy:.1f} vs Noise Floor: {self.ambient_baseline:.1f}) — Recording phrase...")
                    
                    full_audio = sd.rec(speech_samples, samplerate=self.sample_rate, channels=1, dtype="int16")
                    sd.wait()

                    # Transcribe using speech_recognition + Google STT
                    raw_bytes = full_audio.tobytes()
                    audio_data = sr.AudioData(raw_bytes, self.sample_rate, 2)

                    try:
                        transcription = self.recognizer.recognize_google(audio_data).strip()
                        print(f"[MIC] 🗣️ Heard: \"{transcription}\"")

                        clean_cmd = self.extract_command(transcription)
                        if self.is_wake_phrase(transcription) or len(transcription.split()) >= 2:
                            print(f"[WAKE WORD] ⚡ Processing Voice Command: \"{clean_cmd}\"")
                            if self.callback:
                                self.callback(clean_cmd or "hello")

                    except sr.UnknownValueError:
                        pass
                    except Exception as e:
                        logger.warning(f"STT error: {e}")

            except Exception as ex:
                logger.error(f"Mic loop error: {ex}")
                time.sleep(0.4)


def get_wakeword_engine(callback: Optional[Callable[[str], None]] = None) -> SovereignWakeWordEngine:
    return SovereignWakeWordEngine(on_command_callback=callback)

