from __future__ import annotations

import json
from typing import Optional

from jarvisx.runtime import JarvisRuntime


class VisionProvider:
    """Stub Vision/OCR provider."""
    
    def extract_context(self, image_data: bytes) -> str:
        # In a real implementation, this would call GPT-4o Vision or Claude 3.5 Sonnet
        # For this stub, we'll try to extract text if it's JSON, otherwise return a default description.
        try:
            payload = json.loads(image_data.decode("utf-8"))
            return str(payload.get("context", "Simulated visual context extracted from image."))
        except (ValueError, UnicodeDecodeError):
            return "Simulated visual context extracted from image."


class VisionManager:
    """Manages the vision pipeline: Image -> VisionProvider -> Edith -> Alfred -> Agent"""
    
    def __init__(
        self,
        runtime: JarvisRuntime,
        vision: Optional[VisionProvider] = None,
    ) -> None:
        self.runtime = runtime
        self.vision = vision or VisionProvider()

    async def process_image_input(self, image_data: bytes, trace_id: Optional[str] = None) -> bytes:
        # 1. Vision/OCR extraction
        text = self.vision.extract_context(image_data)
        
        # 2. Handoff to Alfred via Edith (as the communication interface), flagging has_image=True
        response = await self.runtime.alfred.process(
            text,
            trace_id=trace_id,
            source="edith",
            has_image=True
        )
        
        # 3. Return a synthesized JSON response (for the /vision API)
        return json.dumps(response.to_dict()).encode("utf-8")
