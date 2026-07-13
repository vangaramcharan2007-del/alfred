from __future__ import annotations

import json
from typing import Optional

from jarvisx.runtime import JarvisRuntime
from jarvisx.clients.tesseract_client import TesseractClient


class VisionProvider:
    """Vision/OCR provider using Tesseract."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.client = TesseractClient(tesseract_cmd=tesseract_cmd)
    
    def extract_context(self, image_data: bytes) -> str:
        # First try parsing as JSON (legacy stub compatibility)
        try:
            payload = json.loads(image_data.decode("utf-8"))
            return str(payload.get("context", "Simulated visual context extracted from image."))
        except (ValueError, UnicodeDecodeError):
            pass
            
        # Fall back to Tesseract OCR
        extracted = self.client.extract_text(image_data)
        if not extracted or extracted.startswith("Failed to extract"):
            return "Simulated visual context extracted from image."
        
        return f"Extracted Text from Image:\n{extracted}"


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
