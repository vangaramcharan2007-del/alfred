"""Alfred Voice Runtime — the single visible entry point for Jarvis X.

Integrates STT, TTS, WakeWord, Mission Engine, and the Dashboard.
"""
import os
import sys
import time
import logging

sys.path.insert(0, os.path.abspath("src"))

from jarvisx.core.voice.tts_engine import TTSEngine
from jarvisx.core.voice.stt_listener import STTListener
from jarvisx.core.voice.wakeword_engine import WakewordEngine
from jarvisx.core.voice.dashboard import MissionDashboard
from jarvisx.core.execution.mission_engine import MissionEngine
from jarvisx.core.capabilities.runtime import CapabilityRuntime
from jarvisx.core.capabilities.registry import SystemCapabilityRegistry
from jarvisx.core.capabilities.base import Capability

logging.basicConfig(level=logging.WARNING)

class VoiceRuntime:
    def __init__(self, use_microphone=True):
        self.dashboard = MissionDashboard()
        self.wakeword = WakewordEngine()
        
        if use_microphone:
            self.stt = STTListener()
        else:
            self.stt = None
            
        self.tts = TTSEngine()
        
        from pathlib import Path
        self.registry = SystemCapabilityRegistry()
        self.registry.discover_plugins(Path("src/jarvisx/core/capabilities/providers"))
        
        self.cap_runtime = CapabilityRuntime(self.registry)
        self.mission_engine = MissionEngine(self.cap_runtime, dashboard=self.dashboard)
        
        self.memory = []

    def run_conversation_loop(self):
        """Main loop — listen, dispatch, speak, repeat."""
        self.dashboard.render()
        
        while True:
            # 1. Wake Word
            self.wakeword.wait_for_wake_word(self.dashboard)
            self.dashboard.set_tts("Yes?")
            self.tts.speak("Yes?")
            self.dashboard.set_tts("")
            self.dashboard.set_listening(True)

            # 2. STT
            if self.stt:
                text = self.stt.listen(timeout=12.0)
            else:
                text = input("\n[MOCK STT] Speak: ")
                
            self.dashboard.set_listening(False)

            if not text:
                continue

            self.dashboard.set_command(text)
            
            # 3. Check for interrupt
            if self.wakeword.check_for_interrupt(text):
                self.dashboard.set_tts("Stopping.")
                self.tts.speak("Stopping.")
                self.dashboard.set_tts("")
                self.dashboard.set_command("")
                continue
                
            if text.lower() == "exit":
                break

            # 4. Alfred (Memory + Planning)
            self._process_command(text)
            
            # Reset
            time.sleep(2)
            self.dashboard.set_command("")
            self.dashboard.set_tts("")

    def _process_command(self, text: str):
        text_lower = text.lower()
        
        # Fake conversational matching for demo
        if "hello" in text_lower or "hi alfred" in text_lower:
            self.dashboard.set_tts("Hello. How may I assist you today?")
            self.tts.speak("Hello. How may I assist you today?")
            return
            
        if "remember" in text_lower:
            self.memory.append(text)
            self.dashboard.add_memory(text)
            self.dashboard.set_tts("I have stored that in memory.")
            self.tts.speak("I have stored that in memory.")
            return
            
        if "what do you remember" in text_lower or "what were we talking about" in text_lower or "continue yesterday" in text_lower:
            if self.memory:
                mem = " and ".join(self.memory)
                self.dashboard.set_tts(f"I remember you said: {mem}")
                self.tts.speak(f"I remember you said: {mem}")
            else:
                self.dashboard.set_tts("I don't have anything in recent memory.")
                self.tts.speak("I don't have anything in recent memory.")
            return

        # Fallthrough to Mission Engine
        self.dashboard.set_tts("Executing mission.")
        self.tts.speak("Executing mission.")
        self.dashboard.set_tts("")
        
        success = self.mission_engine.execute_mission(text)
        
        if success:
            self.dashboard.set_tts("Mission completed successfully.")
            self.tts.speak("Mission completed successfully.")
        else:
            self.dashboard.set_tts("Mission failed or could not be planned.")
            self.tts.speak("Mission failed or could not be planned.")


def main():
    runtime = VoiceRuntime(use_microphone=True)
    try:
        runtime.run_conversation_loop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
