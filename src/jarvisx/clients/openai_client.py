import json
import os
import urllib.request
import urllib.error
from typing import Optional


class OpenAIClient:
    """Minimal dependency-free client for OpenAI APIs."""
    
    API_BASE = "https://api.openai.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def transcribe(self, audio_data: bytes, filename: str = "audio.wav") -> Optional[str]:
        if not self.is_configured:
            return None
            
        url = f"{self.API_BASE}/audio/transcriptions"
        
        # Simple multipart/form-data payload construction
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        
        body = bytearray()
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="model"\r\n\r\nwhisper-1\r\n'.encode("utf-8"))
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(audio_data)
        body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }
        
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("text")
        except Exception:
            return None
