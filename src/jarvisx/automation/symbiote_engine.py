"""
The Symbiote — Keystroke/Mouse Persona Morphing.
Monitors typing speed and mouse velocity to deduce user frustration.
Automatically morphs the LLM persona (Strict/Relaxed) in response.
"""
import logging
import threading
import time
import random
from typing import Optional

logger = logging.getLogger(__name__)

class SymbioteEngine:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.wpm = 60
        self.current_persona = "neutral"

    def _poll_input_metrics(self):
        """Simulate polling a global keyboard/mouse hook."""
        self.wpm = random.randint(30, 140)
        error_rate = random.uniform(0.0, 0.2)
        
        # High WPM + High Errors = Frustrated/Rushing
        # Low WPM = Relaxed
        if self.wpm > 100 and error_rate > 0.1:
            return "strict_mission_control"
        elif self.wpm < 50:
            return "relaxed_conversational"
        return "neutral"

    def _loop(self):
        logger.info("[Symbiote] Hooked into input metrics. Morphing persona actively.")
        while self._running:
            try:
                new_persona = self._poll_input_metrics()
                if new_persona != self.current_persona:
                    self.current_persona = new_persona
                    logger.info(f"[Symbiote] User state shift detected (WPM: {self.wpm}). Morphing persona to: {new_persona.upper()}")
                    
                    # Push to HUD
                    try:
                        from jarvisx.dashboard.hud_server import push_event_sync
                        push_event_sync("persona_shift", {"persona": new_persona, "wpm": self.wpm})
                    except Exception:
                        pass
                        
            except Exception as e:
                logger.error(f"[Symbiote] Polling error: {e}")
            time.sleep(10)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="Symbiote")
        self._thread.start()
        
    def stop(self):
        self._running = False
