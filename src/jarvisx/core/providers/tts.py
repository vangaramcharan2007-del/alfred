import os
from jarvisx.core.providers.provider_registry import BaseProvider, ProviderCapability
from jarvisx.clients.elevenlabs_client import ElevenLabsClient


class ElevenLabsProvider(BaseProvider):
    def __init__(self):
        self.client = ElevenLabsClient()
        
    @property
    def capability(self) -> ProviderCapability:
        # Priority 1: ElevenLabs
        return ProviderCapability("TTS", "ElevenLabs", 10, False)
        
    async def check_health(self) -> bool:
        return self.client.is_configured
        
    async def benchmark(self) -> float:
        return 120.0 if self.client.is_configured else float('inf')
        
    def synthesize(self, text: str, voice_id: str = ElevenLabsClient.VOICE_ALFRED) -> bytes:
        return self.client.synthesize(text, voice_id) or b""


class Pyttsx3Provider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        # Priority 2: pyttsx3
        return ProviderCapability("TTS", "pyttsx3", 20, True)
        
    async def check_health(self) -> bool:
        return True
        
    async def benchmark(self) -> float:
        return 50.0
        
    def synthesize(self, text: str, voice_id: str = "") -> bytes:
        return f"[pyttsx3 TTS] {text}".encode("utf-8")


class EdgeTTSProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        # Priority 3: Edge TTS
        return ProviderCapability("TTS", "Edge TTS", 30, False)
        
    async def check_health(self) -> bool:
        return True
        
    async def benchmark(self) -> float:
        return 150.0
        
    def synthesize(self, text: str, voice_id: str = "") -> bytes:
        return f"[Edge TTS] {text}".encode("utf-8")


class SystemTTSProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        # Priority 4: System TTS
        return ProviderCapability("TTS", "System TTS", 40, True)
        
    async def check_health(self) -> bool:
        return True
        
    async def benchmark(self) -> float:
        return 40.0
        
    def synthesize(self, text: str, voice_id: str = "") -> bytes:
        return f"[System TTS] {text}".encode("utf-8")
