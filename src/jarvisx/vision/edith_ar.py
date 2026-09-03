"""
E.D.I.T.H. AR Engine — Augmented Reality & Vision Engine.
Provides real-time screen awareness using mss and Gemini 3.6 Flash Vision.
Allows Eevee to "see" what the user is doing to provide contextual nudges.

Phase 12: REAL VISION — Actually captures screen and sends to Cloud LLM.
"""
import logging
import threading
import time
import asyncio
from typing import Optional

try:
    import mss
    from PIL import Image
    HAS_VISION_DEPS = True
except ImportError:
    HAS_VISION_DEPS = False

logger = logging.getLogger(__name__)

class EdithAREngine:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._gemini = None

    def _push_to_ui(self, event_type: str, data: dict):
        """Broadcast events to E.V. UI."""
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def get_gemini(self):
        if not self._gemini:
            try:
                from jarvisx.llm.gemini_provider import GeminiLLMProvider
                self._gemini = GeminiLLMProvider()
            except Exception as e:
                logger.error(f"[E.D.I.T.H.] Failed to load Gemini Provider: {e}")
        return self._gemini

    def capture_screen_image(self) -> Optional['Image.Image']:
        if not HAS_VISION_DEPS:
            logger.warning("[E.D.I.T.H.] Missing 'mss' or 'Pillow'. Cannot capture screen.")
            return None
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # primary monitor
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                # Downscale to save bandwidth/tokens
                img.thumbnail((1280, 720))
                return img
        except Exception as e:
            logger.error(f"[E.D.I.T.H.] Screen capture failed: {e}")
            return None

    def analyze_screen(self, prompt: str = "Describe what the user is doing on their screen briefly.") -> str:
        """Takes a screenshot, sends it to Gemini Flash, and returns a summary."""
        logger.info("[E.D.I.T.H.] Capturing visual telemetry...")
        self._push_to_ui("edith_event", {"action": "Capturing screen telemetry..."})
        
        img = self.capture_screen_image()
        if not img:
            return "Unable to capture screen. Vision sensors offline."

        gemini = self.get_gemini()
        if not gemini:
            return "Vision LLM offline."

        # We must run the async generate function in a sync wrapper since this is called from threads
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Build multimodal contents
        contents = [img, prompt]
        
        logger.info("[E.D.I.T.H.] Uploading frame to Gemini Cloud Route...")
        try:
            res = loop.run_until_complete(
                gemini.generate(
                    prompt="",  # Unused since contents is provided
                    model="gemini-1.5-flash",  # Fast vision model
                    contents=contents
                )
            )
            analysis = res.get("response", "No analysis returned.")
            logger.info(f"[E.D.I.T.H.] Analysis Complete: {analysis}")
            self._push_to_ui("edith_event", {"action": "Analysis Complete", "result": analysis})
            return analysis
        except Exception as e:
            logger.error(f"[E.D.I.T.H.] Analysis failed: {e}")
            return f"Error analyzing screen: {e}"

    def _loop(self):
        logger.info("[E.D.I.T.H.] Vision Protocol Online.")
        self._push_to_ui("module_boot", {"name": "EdithAREngine", "status": "ONLINE (VISION READY)"})
        
        while self._running:
            time.sleep(1)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="EDITH")
        self._thread.start()
        
    def stop(self):
        self._running = False
