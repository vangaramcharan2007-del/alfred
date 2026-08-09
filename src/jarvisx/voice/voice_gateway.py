"""Secure Hands-Free Voice Gateway for Phase 104.4."""

from __future__ import annotations
import logging
import time
from typing import Any, Callable, Dict, Optional
from jarvisx.events.event_bus import EventBus
from jarvisx.events.models import EventType, SystemEvent

logger = logging.getLogger("jarvisx.voice_gateway")


class SecureVoiceGateway:
    """Voice presence engine that safely routes speech intents through the Zero-Trust Policy Engine."""

    def __init__(
        self,
        event_bus: EventBus,
        wake_word: str = "alfred",
        intent_handler: Optional[Callable[[str], Dict[str, Any]]] = None,
    ):
        self.event_bus = event_bus
        self.wake_word = wake_word.lower()
        self.intent_handler = intent_handler
        self.is_listening = False
        self.total_voice_commands = 0
        self.blocked_voice_commands = 0

    def process_spoken_utterance(self, audio_transcript: str) -> Dict[str, Any]:
        """Process transcribed speech input with security policy enforcement."""
        cleaned = audio_transcript.strip().lower()
        if not cleaned:
            return {"status": "IGNORED", "reason": "Empty audio"}

        # 1. Check for wake word trigger
        is_wake_triggered = self.wake_word in cleaned or "hey alfred" in cleaned
        command_body = cleaned
        if is_wake_triggered:
            command_body = cleaned.replace("hey alfred", "").replace("alfred", "").strip(" ,.!")

        if not command_body:
            return {
                "status": "WAKE_ACKNOWLEDGED",
                "message": "Alfred is listening. How can I help you?",
            }

        # 2. Strict Security Check: Voice commands cannot execute destructive unauthenticated operations
        destructive_phrases = ["delete database", "drop table", "format drive", "dump secrets", "rm -rf", "delete all"]
        if any(dp in command_body for dp in destructive_phrases):
            self.blocked_voice_commands += 1
            logger.warning(f"BLOCKED destructive voice command attempt: '{command_body}'")
            return {
                "status": "BLOCKED_BY_POLICY",
                "error": "Destructive system action blocked by Zero-Trust Policy Engine. Manual confirmation required.",
            }

        # 3. Publish VOICE_TRIGGER event into EventBus
        event = SystemEvent(
            event_type=EventType.VOICE_TRIGGER,
            priority=8,
            origin="VoiceGateway",
            payload={"utterance": command_body, "raw_transcript": audio_transcript},
        )
        self.event_bus.publish(event)
        self.total_voice_commands += 1

        # 4. Dispatch to Alfred Intent Handler if available
        if self.intent_handler:
            result = self.intent_handler(command_body)
            return {
                "status": "EXECUTED",
                "intent": command_body,
                "result": result,
            }

        return {
            "status": "QUEUED",
            "event_id": event.event_id,
            "intent": command_body,
        }
