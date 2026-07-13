from __future__ import annotations

import json
import io
from typing import Optional, Dict, Any

try:
    import cv2
    import numpy as np
    from PIL import Image
    import pyautogui
except ImportError:
    cv2 = None
    np = None
    Image = None
    pyautogui = None

from jarvisx.runtime import JarvisRuntime
from jarvisx.clients.tesseract_client import TesseractClient


class VisionProvider:
    """Vision/OCR provider using Tesseract."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.client = TesseractClient(tesseract_cmd=tesseract_cmd)
    def capture_screenshot(self) -> Optional[bytes]:
        """Captures a screenshot of the primary display."""
        if not pyautogui or not Image:
            return None
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    def analyze_gui(self, image_data: bytes) -> Dict[str, Any]:
        """Uses OpenCV to detect potential windows, buttons, or bounding boxes."""
        if not cv2 or not np:
            return {"error": "OpenCV not installed"}
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            windows = 0
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 200 and h > 200:  # simplistic window threshold
                    windows += 1
                    
            return {"detected_windows": windows, "resolution": f"{img.shape[1]}x{img.shape[0]}"}
        except Exception as e:
            return {"error": str(e)}

    def extract_context(self, image_data: bytes) -> str:
        # First try parsing as JSON (legacy stub compatibility)
        try:
            payload = json.loads(image_data.decode("utf-8"))
            return str(payload.get("context", "Simulated visual context extracted from image."))
        except (ValueError, UnicodeDecodeError):
            pass
            
        gui_info = self.analyze_gui(image_data)
        gui_str = f"GUI Analysis: {json.dumps(gui_info)}\n"
            
        # Fall back to Tesseract OCR
        extracted = self.client.extract_text(image_data)
        if not extracted or extracted.startswith("Failed to extract"):
            return f"{gui_str}Simulated visual context extracted from image."
        
        return f"{gui_str}Extracted Text from Image:\n{extracted}"


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
