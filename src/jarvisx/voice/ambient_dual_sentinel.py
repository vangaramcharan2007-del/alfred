"""
Ambient Dual-Voice Listener & Proactive Coding Sentinel for Alfred & E-V.
========================================================================
1. Listens continuously for "Alfred" (Batman Butler) and "E-V" (Ava Co-Pilot) wake words.
2. Proactively detects coding tracebacks, compiler errors, and DSA bugs.
3. 100% Headless & Voice-to-Voice: Never opens UI windows unless asked ("open UI").
"""

import os
import sys
import time
import logging
import threading
import sounddevice as sd
import numpy as np
import speech_recognition as sr
import pyperclip

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from jarvisx.voice.sovereign_neural_tts import SovereignNeuralTTS
from jarvisx.automation.ev_neural_voice import speak_ev_neural
from jarvisx.organism import get_organism

logger = logging.getLogger("jarvisx.ambient_sentinel")


class AmbientDualSentinel:
    """Continuous Background Wake-Word & Proactive Coding Assistant."""

    _instance = None

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.is_running = False
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.alfred_mouth = SovereignNeuralTTS(default_voice_key="british_butler", rate="-4%", pitch="-4Hz")
        self._last_clipboard = ""
        self._known_errors_seen = set()

    @classmethod
    def get_instance(cls) -> "AmbientDualSentinel":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start(self):
        """Starts ambient background listening and coding monitoring."""
        if self.is_running:
            return
        self.is_running = True
        
        # Thread 1: Continuous Wake-Word Audio Listener
        threading.Thread(target=self._ambient_audio_loop, daemon=True, name="AmbientWakeWordThread").start()
        
        # Thread 2: Proactive Coding Error Watcher
        threading.Thread(target=self._coding_error_watcher_loop, daemon=True, name="ProactiveCodingWatcher").start()
        
        print("[+] Ambient Dual-Voice Sentinel & Proactive Coding Watcher active.")

    def _ambient_audio_loop(self):
        """Continuous background audio listening loop."""
        print("[*] Ambient Ear listening for 'Alfred' and 'E-V' wake words...")
        while self.is_running:
            try:
                # Capture audio snippet via sounddevice
                duration_sec = 3.5
                recording = sd.rec(int(duration_sec * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='int16')
                sd.wait()

                # Check if energy above baseline
                rms = np.sqrt(np.mean(recording.astype(np.float32) ** 2))
                if rms < 150:  # Silence
                    continue

                # Transcribe speech
                raw_data = recording.tobytes()
                audio_data = sr.AudioData(raw_data, self.sample_rate, 2)
                try:
                    text = self.recognizer.recognize_google(audio_data).lower().strip()
                except (sr.UnknownValueError, sr.RequestError):
                    continue

                if not text:
                    continue

                print(f"🎙️ [VOICE HEARD]: \"{text}\"")

                # 1. Alfred Wake-Word Trigger
                if "alfred" in text or "butler" in text:
                    self._handle_alfred_wake(text)

                # 2. E-V Wake-Word Trigger
                elif "ev" in text or "e-v" in text or "ivy" in text or "hey v" in text:
                    self._handle_ev_wake(text)

            except Exception as e:
                time.sleep(1.0)

    def _handle_alfred_wake(self, text: str):
        """Handles Alfred Batman Butler interactions."""
        cmd = text.replace("alfred", "").replace("hey", "").strip()
        if not cmd:
            self.alfred_mouth.speak("At your service, Master Charan. How may I assist you, Sir?")
            return

        print(f"🦇 [ALFRED REACTING]: \"{cmd}\"")
        if "open ui" in cmd or "open hud" in cmd:
            self.alfred_mouth.speak("Opening the Situation Deck for you now, Sir.")
            org = get_organism()
            org.hands.act("open_app", {"application": "hud"})
        else:
            # Route to Organism ReAct loop
            import asyncio
            org = get_organism()
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(org.react_turn(cmd))
                else:
                    loop.run_until_complete(org.react_turn(cmd))
            except Exception:
                asyncio.run(org.react_turn(cmd))

    def _handle_ev_wake(self, text: str):
        """Handles E-V Co-Pilot interactions."""
        cmd = text.replace("ev", "").replace("e-v", "").replace("hey", "").replace("ivy", "").strip()
        if not cmd:
            speak_ev_neural("I am right here, boss! Ready to solve math or debug code!")
            return

        print(f"🕷️ [E-V REACTING]: \"{cmd}\"")
        if "math" in cmd or "heat" in cmd or "wave" in cmd or "solve" in cmd:
            from jarvisx.automation.ev_master_automation_engine import EVMasterAutomationEngine
            EVMasterAutomationEngine.get_instance().level_2_screen_vision_solve()
        elif "cool" in cmd:
            from jarvisx.automation.ev_master_automation_engine import EVMasterAutomationEngine
            EVMasterAutomationEngine.get_instance().level_5_turbo_cool()
        else:
            speak_ev_neural(f"On it, boss! Processing {cmd}!")

    def _coding_error_watcher_loop(self):
        """Proactively detects stack traces, syntax errors, and coding bugs."""
        while self.is_running:
            try:
                time.sleep(1.5)
                clip = pyperclip.paste().strip()
                if clip and clip != self._last_clipboard:
                    self._last_clipboard = clip
                    
                    # Detect programming errors & tracebacks
                    error_signatures = [
                        "Traceback (most recent call last)",
                        "SyntaxError:",
                        "IndexError:",
                        "KeyError:",
                        "TypeError:",
                        "ZeroDivisionError:",
                        "AttributeError:",
                        "NameError:",
                        "Segmentation fault",
                        "NullPointerException",
                        "Compilation failed"
                    ]

                    for sig in error_signatures:
                        if sig in clip and clip not in self._known_errors_seen:
                            self._known_errors_seen.add(clip)
                            print(f"\n🐛 [PROACTIVE CODING ASSISTANT] Error detected: {sig}")
                            
                            # Extract error line and message
                            lines = clip.splitlines()
                            err_line = next((l for l in reversed(lines) if any(s in l for s in error_signatures)), "Coding error detected")
                            
                            speak_ev_neural(f"I spotted a coding bug on your screen, boss! It looks like a {err_line.split(':')[0]}. Would you like me to suggest the fix?")
                            break

            except Exception:
                pass


def launch_ambient_sentinel():
    sentinel = AmbientDualSentinel.get_instance()
    sentinel.start()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    launch_ambient_sentinel()
