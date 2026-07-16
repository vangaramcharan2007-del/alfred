import logging
import asyncio
from typing import Callable

from .wake_engine import WakeEngine
from .stt_engine import STTEngine
from .tts_engine import TTSEngine
from .voice_registry import VoiceRegistry
from jarvisx.core.memory import SessionManager, ConversationStore

logger = logging.getLogger(__name__)

class InteractionLoop:
    def __init__(self, voice_router=None, state_callback: Callable[[str], None] = None, transcript_callback: Callable[[str, bool], None] = None):
        self.registry = VoiceRegistry()
        self.wake = WakeEngine(threshold=0.70)
        self.stt = STTEngine(confidence_threshold=0.50)
        self.tts = TTSEngine(self.registry)
        self.voice_router = voice_router
        
        self.session_manager = SessionManager()
        self.conv_store = ConversationStore()
        
        self.state_callback = state_callback
        self.transcript_callback = transcript_callback
        
        self.is_running = False
        self._loop_task = None
        self._interrupt_flag = False

    def initialize(self):
        self.wake.initialize()
        self.stt.initialize()
        self.tts.initialize()

    async def start(self):
        self.is_running = True
        self._loop_task = asyncio.create_task(self._loop())

    async def stop(self):
        self.is_running = False
        if self._loop_task:
            self._loop_task.cancel()
        self.wake.cleanup()
        self.stt.cleanup()
        self.tts.stop()
        self.session_manager.mark_clean_shutdown()

    def _set_state(self, state: str):
        logger.info(f"UI State -> {state}")
        if self.state_callback:
            self.state_callback(state)

    def _add_transcript(self, text: str, is_user: bool = False):
        speaker = "user" if is_user else "alfred"
        session_id = self.session_manager.get_session_id()
        self.conv_store.log_transcript(session_id, speaker, text)
        
        if self.transcript_callback:
            self.transcript_callback(text, is_user)

    async def _loop(self):
        self._set_state("sleeping")
        
        while self.is_running:
            try:
                # 1. Wait for Wake Word
                detected = await self.wake.wait_for_wake()
                if not detected or not self.is_running:
                    continue

                # Wake detected, play a subtle chime or just change state
                self._set_state("listening")
                
                # 2. Record and Transcribe
                text = await self.stt.listen_and_transcribe()
                if not text:
                    self._set_state("sleeping")
                    continue

                text_lower = text.lower()
                self._add_transcript(text, is_user=True)

                # Check for interrupt
                if "alfred stop" in text_lower or "stop alfred" in text_lower:
                    self.tts.stop()
                    self._set_state("sleeping")
                    continue

                # 3. Think / Route
                self._set_state("thinking")
                
                # Fallback response if confidence is low (STT length check as proxy for now)
                if len(text.split()) < 2 and "hello" not in text_lower:
                     self._set_state("speaking")
                     await self.tts.speak("I didn't catch that. Could you repeat it?", "alfred")
                     self._set_state("sleeping")
                     continue

                # Delegate to Voice Router (Alfred/Hermes)
                if self.voice_router:
                    response_text = await self.voice_router.process_voice_command(text)
                else:
                    response_text = "I'm sorry, my logic core is disconnected."

                # 4. Speak response
                self._set_state("speaking")
                self._add_transcript(response_text, is_user=False)
                await self.tts.speak(response_text, "alfred")

                self._set_state("sleeping")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in Interaction Loop: {e}")
                self._set_state("error")
                await asyncio.sleep(2)
                self._set_state("sleeping")
