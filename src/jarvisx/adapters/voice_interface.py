from __future__ import annotations

import asyncio
import json
from typing import Optional

from jarvisx.runtime import JarvisRuntime
from jarvisx.clients.elevenlabs_client import ElevenLabsClient
from jarvisx.clients.openai_client import OpenAIClient


class STTProvider:
    """Speech-to-Text provider with OpenAI Whisper + Stub fallback."""
    
    def __init__(self, client: Optional[OpenAIClient] = None):
        self.client = client or OpenAIClient()
        
    def transcribe(self, audio_data: bytes) -> str:
        if self.client.is_configured:
            transcription = self.client.transcribe(audio_data)
            if transcription:
                return transcription
                
        # Fallback to stub parsing for tests or offline
        try:
            payload = json.loads(audio_data.decode("utf-8"))
            return str(payload.get("text", "Simulated voice input text"))
        except (ValueError, UnicodeDecodeError):
            return "Simulated voice input text"


class TTSProvider:
    """Text-to-Speech provider with ElevenLabs + Stub fallback."""
    
    def __init__(self, client: Optional[ElevenLabsClient] = None):
        self.client = client or ElevenLabsClient()
        
    def synthesize(self, text: str, agent_id: str, mode_config: dict[str, object]) -> bytes:
        if self.client.is_configured:
            voice_id = ElevenLabsClient.VOICE_ALFRED
            if agent_id == "edith":
                voice_id = ElevenLabsClient.VOICE_EDITH
                
            audio_out = self.client.synthesize(text, voice_id=voice_id)
            if audio_out:
                return audio_out
                
        # Fallback stub implementation
        metadata = {
            "text": text,
            "voice_profile": agent_id,
            "mode_config": mode_config,
            "status": "synthesized"
        }
        return json.dumps(metadata).encode("utf-8")


class VoiceManager:
    """Manages the audio pipeline: Audio -> STT -> Edith -> Alfred -> Agent -> TTS -> Audio Out"""
    
    def __init__(self, runtime: JarvisRuntime) -> None:
        self.runtime = runtime
        self._current_task = None
        self._interrupted = asyncio.Event()

    def interrupt(self) -> None:
        """Triggers an interruption of the current voice processing."""
        self._interrupted.set()
        if self._current_task:
            self._current_task.cancel()

    async def process_voice_input(self, audio_data: bytes, trace_id: Optional[str] = None) -> bytes:
        self._interrupted.clear()
        
        async def _process():
            # 1. Speech-to-Text ingestion (via router)
            text = await self.runtime.provider_router.route_with_failover("STT", "transcribe", audio_data)
            if asyncio.iscoroutine(text):
                text = await text
            if not text:
                text = "Simulated voice input text"
                
            if self._interrupted.is_set():
                raise asyncio.CancelledError()
            
            # 2. Handoff to Alfred via Edith
            response = await self.runtime.alfred.process(
                text,
                trace_id=trace_id,
                source="edith"
            )
            
            if self._interrupted.is_set():
                raise asyncio.CancelledError()
            
            # 3. Extract agent and mode for TTS
            agent_id = response.agent_id
            mode_config = {}
            if isinstance(response.data, dict):
                if "orchestrator_response_config" in response.data:
                    mode_config = response.data["orchestrator_response_config"]
                elif "response_config" in response.data:
                    mode_config = response.data["response_config"]
            
            # 4. Text-to-Speech synthesis (via router)
            voice_config = self.runtime.config_manager.get(f"voices.{agent_id}", {})
            voice_id = voice_config.get("voice_id", "default")
            
            # Simulated streaming by yielding chunks (if router supports it, else we await full)
            audio_out = await self.runtime.provider_router.route_with_failover("TTS", "synthesize", response.message, voice_id=voice_id)
            if asyncio.iscoroutine(audio_out):
                audio_out = await audio_out
                
            return audio_out

        try:
            import asyncio
            self._current_task = asyncio.create_task(_process())
            return await self._current_task
        except asyncio.CancelledError:
            self.runtime.alfred.logger.write("info", "voice.interrupted", trace_id=trace_id)
            return b""
        finally:
            self._current_task = None
