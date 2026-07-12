from __future__ import annotations

import json
from typing import Optional

from jarvisx.runtime import JarvisRuntime


class STTProvider:
    """Stub Speech-to-Text provider."""
    
    def transcribe(self, audio_data: bytes) -> str:
        # In a real implementation, this would call Whisper, Deepgram, etc.
        # For this stub, we'll try to extract text if it's JSON, otherwise return a default.
        try:
            payload = json.loads(audio_data.decode("utf-8"))
            return str(payload.get("text", "Simulated voice input text"))
        except (ValueError, UnicodeDecodeError):
            return "Simulated voice input text"


class TTSProvider:
    """Stub Text-to-Speech provider."""
    
    def synthesize(self, text: str, agent_id: str, mode_config: dict[str, object]) -> bytes:
        # In a real implementation, this would call ElevenLabs, OpenAI TTS, etc.
        # We respect agent_id for the voice profile and mode_config for pacing.
        metadata = {
            "text": text,
            "voice_profile": agent_id,
            "mode_config": mode_config,
            "status": "synthesized"
        }
        return json.dumps(metadata).encode("utf-8")


class VoiceManager:
    """Manages the audio pipeline: Audio -> STT -> Edith -> Alfred -> Agent -> TTS -> Audio Out"""
    
    def __init__(
        self,
        runtime: JarvisRuntime,
        stt: Optional[STTProvider] = None,
        tts: Optional[TTSProvider] = None
    ) -> None:
        self.runtime = runtime
        self.stt = stt or STTProvider()
        self.tts = tts or TTSProvider()

    async def process_voice_input(self, audio_data: bytes, trace_id: Optional[str] = None) -> bytes:
        # 1. Speech-to-Text ingestion
        text = self.stt.transcribe(audio_data)
        
        # 2. Handoff to Alfred via Edith (as the communication interface)
        response = await self.runtime.alfred.process(
            text,
            trace_id=trace_id,
            source="edith"
        )
        
        # 3. Extract agent and mode for TTS
        agent_id = response.agent_id
        mode_config = {}
        if isinstance(response.data, dict):
            if "orchestrator_response_config" in response.data:
                mode_config = response.data["orchestrator_response_config"]
            elif "response_config" in response.data:
                mode_config = response.data["response_config"]
        
        # 4. Text-to-Speech synthesis
        audio_out = self.tts.synthesize(response.message, agent_id, mode_config)
        return audio_out
