"""
Omni-Clicker — Vision-Based UI Control for Jarvis X.
Captures the screen, asks an LLM vision model to locate UI elements,
and clicks/types using pyautogui.
"""

import io
import re
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class OmniClicker:
    """Vision-grounded UI automation. Finds and interacts with UI elements by description."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "OmniClicker":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.vision_model = "llava"  # or llama3.2-vision if available

    def _capture_screen(self) -> bytes:
        """Capture full screen as PNG bytes."""
        from PIL import ImageGrab
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def _get_screen_size(self) -> Tuple[int, int]:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        return img.size  # (width, height)

    def _ask_vision(self, image_bytes: bytes, prompt: str) -> str:
        """Send screenshot + prompt to vision LLM."""
        import ollama
        import base64
        
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        
        res = ollama.chat(
            model=self.vision_model,
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [b64],
            }]
        )
        return res["message"]["content"]

    def _parse_coordinates(self, response: str, screen_w: int, screen_h: int) -> Optional[Tuple[int, int]]:
        """Extract x,y coordinates from LLM response."""
        # Try patterns like (x, y), x=123 y=456, coordinates: 123, 456
        patterns = [
            r'\((\d+)\s*,\s*(\d+)\)',
            r'x\s*[=:]\s*(\d+).*?y\s*[=:]\s*(\d+)',
            r'(\d{2,4})\s*,\s*(\d{2,4})',
        ]
        for p in patterns:
            m = re.search(p, response, re.IGNORECASE)
            if m:
                x, y = int(m.group(1)), int(m.group(2))
                if 0 <= x <= screen_w and 0 <= y <= screen_h:
                    return (x, y)
        
        # Try percentage-based (e.g. "50%, 75%")
        pct = re.findall(r'(\d+)%', response)
        if len(pct) >= 2:
            x = int(int(pct[0]) / 100 * screen_w)
            y = int(int(pct[1]) / 100 * screen_h)
            return (x, y)
        
        return None

    def find_element(self, description: str) -> Dict[str, Any]:
        """Locate a UI element on screen by natural language description."""
        try:
            img = self._capture_screen()
            w, h = self._get_screen_size()

            prompt = (
                f"Look at this screenshot. Find the UI element described as: '{description}'. "
                f"The screen resolution is {w}x{h}. "
                f"Return the EXACT pixel coordinates (x, y) of the CENTER of that element. "
                f"Format: (x, y)"
            )

            response = self._ask_vision(img, prompt)
            coords = self._parse_coordinates(response, w, h)

            if coords:
                return {"status": "found", "x": coords[0], "y": coords[1], "raw": response}
            return {"status": "not_found", "raw": response}
        except Exception as e:
            logger.error(f"[OmniClicker] find_element failed: {e}")
            return {"status": "error", "error": str(e)}

    def click_element(self, description: str) -> Dict[str, Any]:
        """Find and click a UI element by description."""
        import pyautogui
        
        result = self.find_element(description)
        if result["status"] == "found":
            pyautogui.click(result["x"], result["y"])
            logger.info(f"[OmniClicker] Clicked ({result['x']}, {result['y']}) for '{description}'")
            return {"status": "clicked", "x": result["x"], "y": result["y"]}
        return result

    def type_into_element(self, description: str, text: str) -> Dict[str, Any]:
        """Find an element, click it, and type text into it."""
        import pyautogui
        
        result = self.click_element(description)
        if result["status"] == "clicked":
            import time
            time.sleep(0.3)
            pyautogui.typewrite(text, interval=0.02)
            return {"status": "typed", "text": text, "x": result["x"], "y": result["y"]}
        return result
