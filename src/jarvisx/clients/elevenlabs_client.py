import json
import os
import urllib.request
import urllib.error
from typing import Optional


class ElevenLabsClient:
    """Minimal dependency-free client for ElevenLabs TTS API."""
    
    API_BASE = "https://api.elevenlabs.io/v1"
    
    # Default Voice IDs
    VOICE_ALFRED = "pNInz6obbfDQGcgMyIGC"  # Example voice ID
    VOICE_EDITH = "EXAVITQu4vr4xnSDxMaL"   # Example voice ID
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def synthesize(self, text: str, voice_id: str = VOICE_ALFRED) -> Optional[bytes]:
        if not self.is_configured:
            return None
            
        url = f"{self.API_BASE}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req) as response:
                return response.read()
        except Exception:
            return None
