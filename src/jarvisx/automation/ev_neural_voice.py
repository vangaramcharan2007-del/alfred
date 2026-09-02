"""
Hyper-Realistic Neural AI Voice Engine for E-V (Microsoft Edge Neural TTS).
===========================================================================
Generates studio-quality, ultra-natural, emotional human female speech
using Microsoft's en-US-AvaNeural / en-US-EmmaNeural models with zero robotic artifacting.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
import edge_tts
import pygame

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ultra-natural, expressive female voices:
# 'en-US-AvaNeural' : Warm, cheerful, expressive young female
# 'en-US-EmmaNeural': Friendly, upbeat, conversational female
# 'en-US-JennyNeural': Clear, lively, assistant
VOICE = "en-US-AvaNeural"


async def generate_speech_audio(text: str, output_path: str, voice: str = VOICE):
    # Ensure E-V is pronounced phonetically as "Ee-vee"
    clean_text = text.replace("EV", "Ee-vee").replace("E-V", "Ee-vee").replace("ev", "Ee-vee")
    communicate = edge_tts.Communicate(clean_text, voice, rate="+5%", pitch="+2Hz")
    await communicate.save(output_path)


def speak_ev_neural(text: str, voice: str = VOICE):
    """Generates and plays ultra-realistic human female speech through speakers."""
    import time
    print(f"[E-V NEURAL VOICE ({voice})] \"{text}\"")
    temp_dir = Path(os.getcwd()) / "var" / "audio"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_mp3 = temp_dir / f"ev_speech_{int(time.time() * 1000)}.mp3"

    try:
        asyncio.run(generate_speech_audio(text, str(temp_mp3), voice))

        # Play audio via Pygame mixer
        try:
            pygame.mixer.init()
        except Exception:
            pass
        pygame.mixer.music.load(str(temp_mp3))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        try:
            os.remove(str(temp_mp3))
        except Exception:
            pass
    except Exception as e:
        print(f"[!] Neural voice online error ({e}) -> Falling back to offline local voice...")
        try:
            from jarvisx.voice.offline_speaker import speak_offline
            speak_offline(text, voice_gender="female")
        except Exception as e2:
            print(f"[!] Offline voice error: {e2}")


if __name__ == "__main__":
    test_msg = sys.argv[1] if len(sys.argv) > 1 else "Hey boss! E-V here! Check out my brand new, ultra-natural voice! How do I sound?"
    speak_ev_neural(test_msg)
