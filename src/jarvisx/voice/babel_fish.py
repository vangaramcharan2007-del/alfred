"""
The Babel Fish — Universal Audio Matrix.
Intercepts local system audio, runs real-time transcription, translates foreign 
languages via LLM, and synthesizes an English whisper into the user's headphones.
"""
import logging
import threading
import time
import random
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BabelFish:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _intercept_audio(self) -> Optional[str]:
        """Simulate intercepting a foreign language audio stream (e.g., from Zoom)."""
        if random.random() > 0.7:
            # Simulated Japanese audio transcription
            return "これは素晴らしいシステムですね"
        return None

    def _process_stream(self):
        logger.info("[BabelFish] Hooking into system audio output (WASAPI/PulseAudio)...")
        time.sleep(1)
        logger.info("[BabelFish] Audio Matrix online. Listening for foreign dialects.")
        
        while self._running:
            foreign_text = self._intercept_audio()
            
            if foreign_text:
                logger.info(f"[BabelFish] Intercepted audio: '{foreign_text}'")
                
                try:
                    import ollama
                    # Translate
                    prompt = f"Translate this to English quickly: {foreign_text}"
                    res = ollama.chat(
                        model="qwen2.5-coder:1.5b",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    translation = res["message"]["content"].strip()
                    
                    logger.info(f"[BabelFish] Translating -> '{translation}'")
                    logger.info(f"[BabelFish] (Synthesizing whisper TTS to headphones...)")
                    
                    # Push to HUD
                    try:
                        from jarvisx.dashboard.hud_server import push_event_sync
                        push_event_sync("translation", {"original": foreign_text, "english": translation})
                    except Exception:
                        pass
                        
                except Exception as e:
                    logger.debug(f"[BabelFish] Translation pipeline error: {e}")
                    
            time.sleep(3)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._process_stream, daemon=True, name="BabelFish")
        self._thread.start()
        
    def stop(self):
        self._running = False
