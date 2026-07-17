"""Voice Event Bus — decides what Alfred should say aloud and forwards to the TTS engine."""
import logging
from typing import Optional
from jarvisx.core.voice.tts_engine import TTSEngine

logger = logging.getLogger(__name__)


# Events that Alfred should speak aloud
_SPEAK_EVENTS = {
    "startup",
    "objective_started",
    "objective_completed",
    "recovery_started",
    "recovery_completed",
    "initiative_detected",
    "proposal_approved",
    "critical_failure",
    "execution_failed",
}

# Events that Alfred must stay silent on
_SILENT_EVENTS = {
    "memory_indexing",
    "cache_cleanup",
    "agent_communication",
    "internal_planning",
    "heartbeat",
    "background_monitoring",
}


class VoiceBus:
    """Receives system events, filters them, and forwards spoken messages to TTSEngine."""

    def __init__(self, tts_engine: Optional[TTSEngine] = None):
        self.tts = tts_engine or TTSEngine()

    def publish(self, event: str, message: str):
        """Publish an event. If it is speakable, Alfred will say the message aloud."""
        if event in _SILENT_EVENTS:
            logger.debug(f"VoiceBus: SILENT event '{event}' suppressed.")
            return

        if event in _SPEAK_EVENTS:
            logger.info(f"VoiceBus: Speaking event '{event}'")
            print(f"[Alfred speaks] {message}")
            self.tts.speak(message)
        else:
            # Unknown event — default to silent
            logger.debug(f"VoiceBus: unclassified event '{event}' suppressed.")
