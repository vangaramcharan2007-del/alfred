"""Alfred Voice Runtime — the single visible entry point for Jarvis X.

Integrates STT, TTS, WakeWord, Mission Engine, and the Dashboard.
"""
import os
import sys
import time
import logging

sys.path.insert(0, os.path.abspath("src"))

from jarvisx.core.voice.tts_manager import TTSManager, TTSPriority
from jarvisx.core.voice.stt_listener import STTListener
from jarvisx.core.voice.wakeword_service import WakeWordService
from jarvisx.core.voice.dashboard import MissionDashboard
from jarvisx.core.execution.mission_engine import MissionEngine
from jarvisx.core.capabilities.runtime import CapabilityRuntime
from jarvisx.core.capabilities.registry import SystemCapabilityRegistry
from jarvisx.core.capabilities.base import Capability

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class VoiceRuntime:
    def __init__(self, use_microphone=True):
        self.dashboard = MissionDashboard()
        self.wakeword = WakeWordService()
        
        if use_microphone:
            self.stt = STTListener()
        else:
            self.stt = None
            
        self.tts = TTSManager(dashboard=self.dashboard)
        
        from pathlib import Path
        self.registry = SystemCapabilityRegistry()
        self.registry.discover_plugins(Path("src/jarvisx/core/capabilities/providers"))
        
        self.cap_runtime = CapabilityRuntime(self.registry)
        self.mission_engine = MissionEngine(self.cap_runtime, dashboard=self.dashboard)
        
        self.memory = []
        self.current_state = "IDLE"

    def set_state(self, new_state: str):
        self.current_state = new_state
        logger.info(f"State transition -> {new_state}")
        # Could also push this state to Dashboard if desired

    def voice_prompt_callback(self, prompt_text: str) -> bool:
        """Callback for PermissionManager to request permission via voice."""
        self.set_state("ASKING_PERMISSION")
        self.tts.speak(prompt_text, priority=TTSPriority.PERMISSION_REQUEST)
        
        # Wait a moment for TTS to finish reading
        time.sleep(2)
        
        self.dashboard.set_listening(True)
        if self.stt:
            response = self.stt.listen(timeout=8.0)
        else:
            response = input("(y/n): ")
        self.dashboard.set_listening(False)
        
        if not response:
            return False
            
        normalized = response.lower()
        if "yes" in normalized or "proceed" in normalized or "go ahead" in normalized or "yup" in normalized:
            self.tts.speak("Permission granted.")
            return True
        else:
            self.tts.speak("Permission denied.")
            return False

    def run_conversation_loop(self):
        """Main continuous runtime loop."""
        self.dashboard.render()
        
        while True:
            try:
                self.set_state("IDLE")
                self.wakeword.wait_for_wake_word(self.dashboard)
                
                self.set_state("SPEAKING")
                self.tts.speak("Yes?")
                
                self.set_state("LISTENING")
                self.dashboard.set_listening(True)
                
                if self.stt:
                    text = self.stt.listen(timeout=10.0)
                else:
                    text = input("\n[MOCK STT] Speak: ")
                    
                self.dashboard.set_listening(False)

                if not text:
                    continue

                self.dashboard.set_command(text)
                
                if self.wakeword.check_for_interrupt(text):
                    self.tts.stop()
                    self.tts.speak("Stopping.", priority=TTSPriority.STOP)
                    self.dashboard.set_command("")
                    continue
                    
                if text.lower() == "exit alfred":
                    # We rarely exit, but allow an escape hatch
                    self.tts.shutdown()
                    break

                self.set_state("THINKING")
                self._process_command(text)
                
            except Exception as e:
                self.set_state("ERROR")
                logger.error(f"Runtime Exception: {e}", exc_info=True)
                self.tts.speak("I encountered an unexpected error.")
            finally:
                time.sleep(1)
                self.dashboard.set_command("")

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

        self.set_state("EXECUTING")
        success = self.mission_engine.execute_mission(text, voice_prompt_callback=self.voice_prompt_callback)
        
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
