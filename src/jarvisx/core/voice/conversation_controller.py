import logging
from .wakeword_engine import WakewordEngine
from .speech_pipeline import SpeechPipeline
from .intent_router import IntentRouter
from .tts_manager import TTSManager
from .voice_context_manager import VoiceContextManager
from .interruption_manager import InterruptionManager
from .confirmation_manager import ConfirmationManager

logger = logging.getLogger(__name__)

class ConversationController:
    """
    The orchestrator for the entire Voice-First Operating Layer.
    Manages the state machine (Listening -> Transcribing -> Routing -> Executing -> Speaking).
    """
    def __init__(self):
        self.wakeword = WakewordEngine()
        self.stt = SpeechPipeline()
        self.router = IntentRouter()
        self.tts = TTSManager()
        self.context = VoiceContextManager()
        self.interruption = InterruptionManager(self.stt, self.tts)
        self.confirmation = ConfirmationManager()
        self.state = "idle"

    async def process_audio_frame(self, frame: bytes):
        """
        Called constantly in the main loop.
        """
        if self.state == "idle":
            if self.wakeword.detect(frame):
                self.state = "listening"
                # Signal STT to begin capturing
                
    def set_state(self, new_state: str):
        logger.debug(f"Conversation State Transition: {self.state} -> {new_state}")
        self.state = new_state
