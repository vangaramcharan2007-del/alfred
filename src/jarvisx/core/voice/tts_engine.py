import logging
import asyncio

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

logger = logging.getLogger(__name__)

class TTSEngine:
    def __init__(self, voice_registry):
        self.registry = voice_registry
        self.is_playing = False
        self._engine = None

    def initialize(self):
        if HAS_PYTTSX3:
            try:
                self._engine = pyttsx3.init()
            except Exception as e:
                logger.error(f"Failed to init pyttsx3 fallback: {e}")
        else:
            logger.warning("pyttsx3 not installed. TTS disabled.")

    async def speak(self, text: str, personality: str = "alfred"):
        """Synthesize and play speech, matching the personality config."""
        self.is_playing = True
        logger.info(f"Speaking as {personality}: {text}")
        
        config = self.registry.get_voice_config(personality)
        provider = config.get("provider", "piper")
        
        # In a full implementation, you would dispatch to Piper TTS or ElevenLabs here.
        # For this MVP, we route to pyttsx3 fallback to ensure it works instantly everywhere.
        await self._speak_fallback(text, config)

        self.is_playing = False

    async def _speak_fallback(self, text: str, config: dict):
        if not self._engine:
            return

        # Adjust speed mapping roughly
        speed = config.get("speed", 1.0)
        self._engine.setProperty('rate', int(150 * speed))
        
        # Run pyttsx3 in an executor so we don't block asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._sync_speak, text)

    def _sync_speak(self, text: str):
        if self._engine:
            self._engine.say(text)
            self._engine.runAndWait()

    def stop(self):
        """Immediately stop current playback."""
        if self._engine and self.is_playing:
            self._engine.stop()
            self.is_playing = False
