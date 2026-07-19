from .voice_sapi import SapiVoiceAdapter

class VoiceManager:
    """
    Manages the active voice engine.
    Supports injecting different backends via the adapter pattern.
    """
    def __init__(self, backend="sapi"):
        if backend == "sapi":
            self.adapter = SapiVoiceAdapter()
        else:
            raise ValueError(f"Unknown voice backend: {backend}")
            
    def announce(self, text: str, block: bool = False):
        print(f"[Alfred Voice] {text}")
        self.adapter.speak(text, block)
