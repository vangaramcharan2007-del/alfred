import logging
import asyncio

logger = logging.getLogger(__name__)

class TTSManager:
    """
    Text-to-Speech manager for streaming responses.
    Supports voice switching (Alfred, Edith, Hermes), emotions, and instant interruption.
    Latency target: < 500ms.
    """
    def __init__(self):
        self.active_voice = "Alfred"
        self.is_speaking = False
        self.personas = {
            "Alfred": "professional mentor",
            "Edith": "companion assistant",
            "Hermes": "operations specialist"
        }

    async def speak(self, text: str, emotion: str = "neutral"):
        """
        Streams audio to speakers.
        """
        self.is_speaking = True
        logger.info(f"TTS ({self.active_voice} - {emotion}): {text}")
        
        # Simulate streaming latency
        await asyncio.sleep(0.1)
        self.is_speaking = False

    def stop_speaking(self):
        """Immediately halts the audio buffer."""
        if self.is_speaking:
            self.is_speaking = False
            logger.info("TTS interrupted and stopped.")
            
    def set_voice(self, voice_name: str):
        if voice_name in self.personas:
            self.active_voice = voice_name
            logger.info(f"Switched TTS persona to {voice_name}")
