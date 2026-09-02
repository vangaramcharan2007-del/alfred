"""
Sovereign Neural Voice & Ultra-Realistic TTS Engine for Alfred OS.
Replaces robotic SAPI5 with Microsoft Neural Voices (Human-like inflection, breathing, and pacing)
supporting English, British Butler, Indian English, and Telugu.
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import threading
import time
from typing import Optional

import edge_tts
import pygame

# Initialize pygame mixer for low-latency audio playback
try:
    pygame.mixer.init(frequency=24000, size=-16, channels=2, buffer=512)
except Exception:
    pass


class SovereignNeuralTTS:
    """Ultra-realistic Neural Text-To-Speech engine using Microsoft Neural voices with offline fallback."""

    VOICES = {
        "british_butler": "en-GB-ThomasNeural",  # Classic dignified mature Batman Butler (Alfred Pennyworth)
        "cybernetic_jarvis": "en-US-ChristopherNeural",
        "indian_english": "en-IN-PrabhatNeural",
        "telugu_male": "te-IN-MohanNeural",
        "telugu_female": "te-IN-ShrutiNeural",
        "assistant_female": "en-US-JennyNeural",
    }

    def __init__(self, default_voice_key: str = "british_butler", rate: str = "-4%", pitch: str = "-4Hz"):
        self.voice = self.VOICES.get(default_voice_key, "en-GB-ThomasNeural")
        self.rate = rate
        self.pitch = pitch
        self.is_speaking = False
        self._lock = threading.Lock()

    def speak(self, text: str, voice_key: Optional[str] = None, blocking: bool = False):
        """Synthesizes text into realistic human speech and plays it."""
        clean = text.strip()
        if not clean:
            return

        chosen_voice = self.VOICES.get(voice_key, self.voice) if voice_key else self.voice

        if blocking:
            asyncio.run(self._synthesize_and_play(clean, chosen_voice))
        else:
            threading.Thread(
                target=lambda: asyncio.run(self._synthesize_and_play(clean, chosen_voice)),
                daemon=True,
                name="NeuralVoiceThread"
            ).start()

    async def _synthesize_and_play(self, text: str, voice: str):
        with self._lock:
            self.is_speaking = True
            temp_file = None
            try:
                # 1. Generate MP3 using Edge Neural TTS
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, f"alfred_voice_{int(time.time() * 1000)}.mp3")

                communicate = edge_tts.Communicate(text, voice, rate=self.rate, pitch=self.pitch)
                await communicate.save(temp_file)

                # 2. Play via PyGame Mixer
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.05)

                pygame.mixer.music.unload()

            except Exception as e:
                # Fallback to local offline Windows SAPI speaker
                try:
                    from jarvisx.voice.offline_speaker import speak_offline
                    speak_offline(text, voice_gender="male")
                except Exception:
                    print(f"[ALFRED VOICE LOG]: {text} ({e})")
            finally:
                self.is_speaking = False
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception:
                        pass

    def stop(self):
        """Immediately interrupts speech."""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except Exception:
            pass
        self.is_speaking = False


_global_neural_tts: Optional[SovereignNeuralTTS] = None


def get_neural_tts() -> SovereignNeuralTTS:
    global _global_neural_tts
    if _global_neural_tts is None:
        _global_neural_tts = SovereignNeuralTTS()
    return _global_neural_tts


if __name__ == "__main__":
    tts = get_neural_tts()
    print("Testing Ultra-Realistic Neural Speech...")
    tts.speak("Good morning, Charan. Alfred Sovereign Neural Engine is now active and speaking with human inflection.", blocking=True)
