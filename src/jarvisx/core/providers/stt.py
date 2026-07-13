from __future__ import annotations

import os
from jarvisx.core.providers.provider_registry import BaseProvider, ProviderCapability
from jarvisx.clients.openai_client import OpenAIClient


class WhisperAPIProvider(BaseProvider):
    def __init__(self):
        self.client = OpenAIClient()
        
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("STT", "Whisper API", 10, False)
        
    async def check_health(self) -> bool:
        return self.client.is_configured
        
    async def benchmark(self) -> float:
        return 200.0 if self.client.is_configured else float('inf')
        
    def transcribe(self, audio_data: bytes) -> str:
        return self.client.transcribe(audio_data) or ""


class FasterWhisperProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("STT", "Faster Whisper", 20, True)
        
    async def check_health(self) -> bool:
        return os.environ.get("FASTER_WHISPER_PATH") is not None
        
    async def benchmark(self) -> float:
        return 400.0 if await self.check_health() else float('inf')
        
    def transcribe(self, audio_data: bytes) -> str:
        return "[Faster Whisper] Transcribed text"


class WhisperCppProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("STT", "whisper.cpp", 30, True)
        
    async def check_health(self) -> bool:
        # Final fallback stub
        return True
        
    async def benchmark(self) -> float:
        return 600.0
        
    def transcribe(self, audio_data: bytes) -> str:
        # Fallback to stub parsing for tests or offline
        import json
        try:
            payload = json.loads(audio_data.decode("utf-8"))
            return str(payload.get("text", "Simulated voice input text"))
        except (ValueError, UnicodeDecodeError):
            return "Simulated voice input text"
