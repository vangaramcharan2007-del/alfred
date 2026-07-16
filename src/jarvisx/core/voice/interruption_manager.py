import logging
from .speech_pipeline import SpeechPipeline
from .tts_manager import TTSManager

logger = logging.getLogger(__name__)

class InterruptionManager:
    """
    Handles voice interruptions (stop, cancel, wait, pause, nevermind).
    Immediately halts TTS output and aborts STT transcription if required.
    """
    def __init__(self, stt: SpeechPipeline, tts: TTSManager):
        self.stt = stt
        self.tts = tts
        self.interruption_words = ["stop", "cancel", "wait", "pause", "nevermind"]

    def handle_interruption(self, text: str) -> bool:
        """
        Checks if the transcribed text is an interruption command.
        Returns True if an interruption was processed.
        """
        text_lower = text.lower().strip().strip('.').strip('!')
        
        if text_lower in self.interruption_words:
            logger.info(f"Interruption detected: '{text_lower}'")
            self.tts.stop_speaking()
            
            if text_lower in ["cancel", "nevermind"]:
                self.stt.abort_transcription()
            
            return True
        return False
