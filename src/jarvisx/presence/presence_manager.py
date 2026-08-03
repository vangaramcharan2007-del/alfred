from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
import inspect
from jarvisx.core.events import Event
from jarvisx.core.hermes import HermesBus
from jarvisx.presence.voice.wake_word import WakeWordDetector
from jarvisx.presence.voice.speech_input import SpeechInputEngine
from jarvisx.presence.voice.speech_output import SpeechOutputEngine
from jarvisx.presence.vision.screen_analyzer import ScreenAnalyzer
from jarvisx.personality.persona import AlfredPersona

class PresenceManager:
    """
    Unified Presence Manager for Jarvis X Multimodal Assistant.
    States: IDLE, LISTENING, THINKING, EXECUTING, SPEAKING
    """
    STATES = ["IDLE", "LISTENING", "THINKING", "EXECUTING", "SPEAKING"]

    def __init__(
        self,
        bus: Optional[HermesBus] = None,
        wake_detector: Optional[WakeWordDetector] = None,
        speech_input: Optional[SpeechInputEngine] = None,
        speech_output: Optional[SpeechOutputEngine] = None,
        screen_analyzer: Optional[ScreenAnalyzer] = None,
        persona: Optional[AlfredPersona] = None
    ):
        self.bus = bus or HermesBus()
        self.wake_detector = wake_detector or WakeWordDetector()
        self.speech_input = speech_input or SpeechInputEngine()
        self.speech_output = speech_output or SpeechOutputEngine()
        self.screen_analyzer = screen_analyzer or ScreenAnalyzer()
        self.persona = persona or AlfredPersona()
        self.current_state = "IDLE"

    def _publish_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        evt = Event(type=event_type, source="presence.manager", payload=payload)
        res = self.bus.publish(evt)
        if inspect.isawaitable(res):
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(res)
                else:
                    loop.run_until_complete(res)
            except Exception:
                pass

    def set_state(self, new_state: str) -> None:
        if new_state in self.STATES:
            self.current_state = new_state
            self._publish_event("presence.state_changed", {"state": new_state, "time": time.time()})

    async def process_multimodal_input(self, text_input: str) -> Dict[str, Any]:
        # 1. Wake word check
        detected, command = self.wake_detector.detect(text_input)
        if not detected:
            command = text_input

        self.set_state("LISTENING")
        self._publish_event("voice.detected", {"text": text_input, "command": command})

        # 2. Vision Context
        self.set_state("THINKING")
        screen_context = self.screen_analyzer.analyze_screen()
        self._publish_event("screen.changed", screen_context)

        # 3. Formulate Speech Response & State
        self.set_state("SPEAKING")
        persona_msg = self.persona.format_response(f"I received your request: '{command}'. Analyzing project context.")
        self.speech_output.speak(persona_msg, stream=False)

        self.set_state("IDLE")

        return {
            "wake_detected": detected,
            "command": command,
            "screen_context": screen_context,
            "response": persona_msg,
            "state": self.current_state
        }

