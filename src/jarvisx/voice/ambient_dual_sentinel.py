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
from jarvisx.automation.ev_neural_voice import speak_ev_neural, async_speak_ev_neural
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
        
        # Continuous Wake-Word Audio Listener (Non-blocking)
        self._start_background_listener()
        
        print("[+] Ambient Dual-Voice Sentinel active.")

    def _start_background_listener(self):
        """Starts continuous non-blocking background audio listener."""
        print("[*] Ambient Ear listening for 'Alfred' and 'E-V' wake words (continuous stream)...")
        try:
            m = sr.Microphone()
            with m as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
            def callback(recognizer, audio):
                if not self.is_running:
                    return
                try:
                    # Attempt speech recognition, handle offline gracefully
                    text = recognizer.recognize_google(audio).lower().strip()
                    if not text: return
                    
                    # Full-Duplex Interruption: If she is speaking and we hear you, cut her off!
                    import jarvisx.voice.audio_state as audio_state
                    if audio_state.IS_SPEAKING:
                        print(f"🎙️ [INTERRUPT DETECTED]: \"{text}\"")
                        audio_state.stop_all_audio()
                        
                    print(f"🎙️ [VOICE HEARD]: \"{text}\"")

                    # 1. Alfred Wake-Word Trigger
                    if "alfred" in text or "butler" in text:
                        self._handle_alfred_wake(text)

                    # 2. E-V Wake-Word Trigger
                    elif any(w in text for w in ["ev", "e-v", "ivy", "hey v", "tv", "eva", "hevy"]):
                        self._handle_ev_wake(text)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    # Silently handle offline or API rate limit issues so daemon doesn't crash
                    pass

            self.stop_listening = self.recognizer.listen_in_background(m, callback)
        except Exception as e:
            print(f"[-] Failed to initialize continuous mic listener: {e}")

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
        cmd = text.replace("ev", "").replace("e-v", "").replace("hey", "").replace("ivy", "").replace("tv", "").replace("eva", "").replace("hevy", "").strip()
        if not cmd:
            async_speak_ev_neural("I am right here, boss! Ready to solve math or debug code!")
            return

        print(f"🕷️ [E-V REACTING]: \"{cmd}\"")
        if "math" in cmd or "heat" in cmd or "wave" in cmd or "solve" in cmd:
            from jarvisx.automation.ev_master_automation_engine import EVMasterAutomationEngine
            EVMasterAutomationEngine.get_instance().level_2_screen_vision_solve()
        elif "cool" in cmd:
            from jarvisx.automation.ev_master_automation_engine import EVMasterAutomationEngine
            EVMasterAutomationEngine.get_instance().level_5_turbo_cool()
        elif any(w in cmd for w in ["check", "watch", "scan", "look"]):
            from jarvisx.automation.ev_omni_screen_sentinel import EVOmniScreenSentinel
            EVOmniScreenSentinel.get_instance().inspect_now()
        else:
            async_speak_ev_neural(f"On it, boss! Processing {cmd}!")

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
