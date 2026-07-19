from abc import ABC, abstractmethod

class BaseVoiceAdapter(ABC):
    """
    Abstract Base Class for Voice Engine Adapters.
    New backends (e.g., Piper, ElevenLabs) should inherit from this.
    """
    
    @abstractmethod
    def speak(self, text: str, block: bool = False):
        """
        Speak the given text.
        If block is False, the voice engine MUST return immediately and speak in the background.
        """
        pass
