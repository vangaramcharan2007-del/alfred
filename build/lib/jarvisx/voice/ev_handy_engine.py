"""
E-V Handy Push-to-Talk Voice Dictation Engine.
=============================================
Inspired by cjpais/Handy (https://github.com/cjpais/Handy):
1. Records voice on push-to-talk hotkey (Alt+V or F7).
2. Transcribes speech locally/online with low latency.
3. Automatically types the transcribed text into the currently active window.
4. If an agent command is detected ("solve math", "turbo cool"), routes to E-V & Alfred!
"""

import os
import sys
import time
import wave
import tempfile
import logging
import threading
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import pyperclip
import pyautogui

pyautogui.FAILSAFE = False

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from jarvisx.automation.ev_neural_voice import speak_ev_neural

logger = logging.getLogger("jarvisx.handy")


class EVHandyVoiceDictationEngine:
    """Push-to-Talk Dictation & Voice Command Injector."""

    _instance = None

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.is_recording = False
        self.audio_frames = []
        self._record_thread = None
        self.recognizer = sr.Recognizer()
        logger.info("[E-V Handy] Push-to-Talk Dictation Engine Initialized.")

    @classmethod
    def get_instance(cls) -> "EVHandyVoiceDictationEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start_recording(self) -> None:
        """Start capturing microphone audio stream."""
        if self.is_recording:
            return
        self.is_recording = True
        self.audio_frames = []
        print("\n🎙️ [HANDY] Listening to your voice... (Speak now)")
        self._record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self._record_thread.start()

    def _record_loop(self):
        def callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"[Handy Audio Status]: {status}")
            if self.is_recording:
                self.audio_frames.append(indata.copy())

        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16', callback=callback):
            while self.is_recording:
                sd.sleep(50)

    def stop_and_transcribe(self) -> str:
        """Stop recording, compile WAV, and transcribe."""
        if not self.is_recording:
            return ""
        self.is_recording = False
        print("🎙️ [HANDY] Processing speech...")

        if not self.audio_frames:
            return ""

        audio_data = np.concatenate(self.audio_frames, axis=0)

        # Write temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            tmp_path = tmp_wav.name

        try:
            with wave.open(tmp_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())

            with sr.AudioFile(tmp_path) as source:
                audio = self.recognizer.record(source)
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"📝 [HANDY TRANSCRIPTION]: \"{text}\"")
                    return text
                except sr.UnknownValueError:
                    print("⚠️ [HANDY]: Could not understand audio.")
                    return ""
                except Exception as e:
                    print(f"⚠️ [HANDY]: Recognition error: {e}")
                    return ""
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    def type_text_into_active_window(self, text: str) -> None:
        """Types the transcribed text directly into the focused application."""
        if not text:
            return
        print(f"⚡ [HANDY] Typing into active window: '{text}'...")
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')

    def execute_push_to_talk_cycle(self, duration_sec: float = 3.5) -> str:
        """Convenience method for testing or fixed-interval voice dictation."""
        self.start_recording()
        time.sleep(duration_sec)
        text = self.stop_and_transcribe()
        if text:
            # Check for direct agent triggers
            t_lower = text.lower()
            if "math" in t_lower or "heat" in t_lower or "wave" in t_lower:
                from jarvisx.agents.transforms_math_agent import TransformsMathAgent
                sol = TransformsMathAgent.get_instance().solve_1d_wave_equation()
                speak_ev_neural(f"Handy voice command received! Solved {sol.topic}, boss!")
            elif "cool" in t_lower or "ram" in t_lower:
                from jarvisx.automation.ev_master_automation_engine import EVMasterAutomationEngine
                EVMasterAutomationEngine.get_instance().level_5_turbo_cool()
            else:
                self.type_text_into_active_window(text)
        return text
