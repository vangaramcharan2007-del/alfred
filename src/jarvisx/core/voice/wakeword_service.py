import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

class WakeWordService:
    """
    Independent service that continuously listens for a wake word.
    Designed to wrap Porcupine or OpenWakeWord for offline, <300ms latency detection.
    """
    def __init__(self, active_word: str = "Alfred"):
        self.active_word = active_word.lower()
        self.supported_words = ["alfred", "jarvis", "edith", "computer"]
        self.is_listening = False

    def start_listening(self):
        self.is_listening = True
        logger.info(f"WakeWordService listening for '{self.active_word}'...")

    def stop_listening(self):
        self.is_listening = False
        
    def detect(self, audio_chunk: bytes) -> bool:
        """
        Simulated detection block. In production, passes audio_chunk to Porcupine.
        """
        return False
        
    def wait_for_wake_word(self, dashboard=None):
        """Blocks until the wake word is detected."""
        if dashboard:
            dashboard.set_wake_word(False)
            
        # Simulated delay or logic for wake word
        # Currently just returns to simulate trigger
        time.sleep(0.5)
        
        if dashboard:
            dashboard.set_wake_word(True)
            
    def check_for_interrupt(self, text: str) -> bool:
        """Checks if the user said 'stop' to interrupt TTS/execution."""
        if not text:
            return False
        normalized = text.lower().strip()
        return normalized in ["stop", "stop alfred", "cancel", "shut up"]
        
    def switch_wakeword(self, new_word: str):
        normalized = new_word.lower()
        if normalized in self.supported_words:
            self.active_word = normalized
            logger.info(f"Wakeword switched to {new_word}")
        else:
            raise ValueError(f"Unsupported wake word: {new_word}")
