from __future__ import annotations

import os
from jarvisx.core.providers.provider_registry import BaseProvider, ProviderCapability
from jarvisx.clients.elevenlabs_client import ElevenLabsClient


class ElevenLabsProvider(BaseProvider):
    def __init__(self):
        self.client = ElevenLabsClient()
        
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("TTS", "ElevenLabs", 10, False)
        
    async def check_health(self) -> bool:
        return self.client.is_configured
        
    async def benchmark(self) -> float:
        return 120.0 if self.client.is_configured else float('inf')
        
    def synthesize(self, text: str, voice_id: str = ElevenLabsClient.VOICE_ALFRED) -> bytes:
        return self.client.synthesize(text, voice_id) or b""


class PiperProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("TTS", "Piper", 20, True)
        
    async def check_health(self) -> bool:
        return os.path.exists("/usr/bin/piper") or os.environ.get("PIPER_PATH") is not None
        
    async def benchmark(self) -> float:
        return 300.0 if await self.check_health() else float('inf')
        
    def synthesize(self, text: str, voice_id: str = "") -> bytes:
        return f"[Piper TTS] {text}".encode("utf-8")


class Pyttsx3Provider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("TTS", "pyttsx3", 30, True)
        
    async def check_health(self) -> bool:
        # Final fallback, always considered "available"
        return True
        
    async def benchmark(self) -> float:
        return 50.0
        
    def synthesize(self, text: str, voice_id: str = "") -> bytes:
        return f"[pyttsx3 TTS] {text}".encode("utf-8")
