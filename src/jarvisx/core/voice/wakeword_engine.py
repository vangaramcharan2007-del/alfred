import logging

logger = logging.getLogger(__name__)

class WakewordEngine:
    """
    Listens continuously for trigger phrases (Alfred, Edith, Jarvis, Computer).
    Designed to wrap Porcupine or OpenWakeWord for offline, <300ms latency detection.
    """
    def __init__(self, active_word: str = "Alfred"):
        self.active_word = active_word
        self.supported_words = ["Alfred", "Jarvis", "Edith", "Computer"]
        self.is_listening = False

    def start_listening(self):
        self.is_listening = True
        logger.info(f"WakewordEngine listening for '{self.active_word}'...")

    def stop_listening(self):
        self.is_listening = False
        
    def detect(self, audio_chunk: bytes) -> bool:
        """
        Simulated detection block. In production, passes audio_chunk to Porcupine.
        """
        # Simulated return
        return False
        
    def wait_for_wake_word(self, dashboard=None):
        """Blocks until the wake word is detected (Simulated for harnessing)."""
        import time
        if dashboard:
            dashboard.set_wake_word(False)
            dashboard.set_listening(True)
            
        time.sleep(0.5)
        
        if dashboard:
            dashboard.set_wake_word(True)
            dashboard.set_listening(False)
            
    def check_for_interrupt(self, text: str) -> bool:
        """Checks if the user said 'stop' to interrupt TTS/execution."""
        normalized = text.lower().strip()
        return normalized in ["stop", "stop alfred", "cancel", "shut up"]
        
    def switch_wakeword(self, new_word: str):
        if new_word in self.supported_words:
            self.active_word = new_word
            logger.info(f"Wakeword switched to {new_word}")
        else:
            raise ValueError(f"Unsupported wake word: {new_word}")
