"""
Omni-Modal Brain — Real-time Video and Audio Processing.
Continuously captures webcam frames and ambient audio for instant multimodal reasoning.
"""
import logging
import threading
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class OmniModalStream:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_frame = None

    def _stream_loop(self):
        """Simulated OpenCV webcam stream capture."""
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            logger.info("[OmniModal] Webcam stream connected.")
            while self._running:
                ret, frame = cap.read()
                if ret:
                    self._last_frame = frame
                time.sleep(0.1) # 10 FPS
            cap.release()
        except ImportError:
            logger.warning("[OmniModal] cv2 not installed. Streaming disabled.")
            while self._running:
                time.sleep(1)
        except Exception as e:
            logger.error(f"[OmniModal] Stream error: {e}")

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._stream_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        self._running = False

    def ask_vision(self, prompt: str) -> Dict[str, Any]:
        """Ask LLava about the current live frame."""
        if self._last_frame is None:
            return {"status": "error", "message": "No frame available"}
            
        import ollama
        import cv2
        import base64
        
        _, buffer = cv2.imencode('.jpg', self._last_frame)
        img_b64 = base64.b64encode(buffer).decode('utf-8')
        
        try:
            res = ollama.chat(
                model="llava",
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": [img_b64]
                }]
            )
            return {"status": "success", "response": res["message"]["content"]}
        except Exception as e:
            return {"status": "error", "error": str(e)}
