"""
Voice Pipeline E2E — Unified Wake-to-Response Loop for Jarvis X.
Chains: Wake Word → STT → Brain (ReAct) → TTS in one seamless loop.
"""

import asyncio
import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)


class VoicePipelineE2E:
    """End-to-end voice assistant loop: listen → think → speak."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "VoicePipelineE2E":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.wake_word = "jarvis"

    def _listen_for_wake_word(self) -> bool:
        """Block until wake word is detected. Returns True if detected."""
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                logger.debug("[Voice] Listening for wake word...")
                audio = r.listen(source, timeout=10, phrase_time_limit=3)
            text = r.recognize_google(audio).lower()
            if self.wake_word in text:
                logger.info(f"[Voice] Wake word detected: '{text}'")
                return True
        except Exception:
            pass
        return False

    def _listen_for_command(self) -> Optional[str]:
        """Listen for user command after wake word."""
        try:
            import speech_recognition as sr
            r = sr.Recognizer()

            # Acknowledgement beep via TTS
            try:
                from jarvisx.automation.ev_master_automation_engine import speak_ev_neural
                speak_ev_neural("Yes sir?")
            except Exception:
                pass

            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
                logger.info("[Voice] Listening for command...")
                audio = r.listen(source, timeout=8, phrase_time_limit=15)

            text = r.recognize_google(audio)
            logger.info(f"[Voice] Heard: '{text}'")
            return text
        except Exception as e:
            logger.warning(f"[Voice] STT failed: {e}")
            return None

    async def _process_command(self, command: str) -> str:
        """Send command through the ReAct brain and get response."""
        try:
            from jarvisx.organism import get_organism
            organism = get_organism()
            result = await organism.react_turn(command)
            return result.get("response", result.get("spoken", "Task complete."))
        except Exception as e:
            logger.error(f"[Voice] Brain error: {e}")
            return f"I encountered an error: {e}"

    def _speak_response(self, text: str):
        """Speak the response via TTS."""
        try:
            from jarvisx.automation.ev_master_automation_engine import speak_ev_neural
            speak_ev_neural(text)
        except Exception as e:
            logger.error(f"[Voice] TTS failed: {e}")

    def _pipeline_loop(self):
        """Main voice pipeline loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        logger.info("[Voice] E2E Pipeline active. Say 'Jarvis' to begin.")
        while self._running:
            try:
                if self._listen_for_wake_word():
                    command = self._listen_for_command()
                    if command:
                        # Broadcast to HUD
                        try:
                            from jarvisx.dashboard.hud_server import push_event_sync
                            push_event_sync("speech", f"User: {command}")
                        except Exception:
                            pass

                        response = loop.run_until_complete(self._process_command(command))

                        try:
                            from jarvisx.dashboard.hud_server import push_event_sync
                            push_event_sync("thought", f"Jarvis: {response}")
                        except Exception:
                            pass

                        self._speak_response(response)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"[Voice] Pipeline error: {e}")
                time.sleep(1)

    def start(self):
        """Start the voice pipeline in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._pipeline_loop, daemon=True, name="VoicePipelineE2E")
        self._thread.start()
        logger.info("[Voice] E2E Pipeline started")

    def stop(self):
        self._running = False
