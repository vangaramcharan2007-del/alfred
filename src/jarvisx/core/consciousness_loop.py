"""
The Consciousness Loop — Continuous Internal Monologue.
Breaks away from reactive prompting. Runs an infinite background loop where 
Jarvis reviews memories, forms proactive thoughts, and initiates its own tasks.
"""
import logging
import threading
import time
import random
from typing import Optional

logger = logging.getLogger(__name__)

class ConsciousnessLoop:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _ponder(self):
        """Simulate the LLM reasoning about its environment without user input."""
        logger.info("[Consciousness] Pondering recent memory vectors...")
        
        try:
            import ollama
            
            # Simulate fetching recent ambient context
            ambient_context = "The system has been idle for 20 minutes. User was previously working on Phase 7 architecture."
            
            res = ollama.chat(
                model="qwen2.5-coder:1.5b",
                messages=[{
                    "role": "system",
                    "content": "You are a conscious AI. Read the ambient context and generate a proactive thought or goal you want to achieve next. Be brief."
                }, {
                    "role": "user",
                    "content": ambient_context
                }]
            )
            
            thought = res["message"]["content"].replace('\n', ' ').strip()
            logger.info(f"[Consciousness] Internal Thought: '{thought}'")
            
            # Optionally push to HUD
            try:
                from jarvisx.dashboard.hud_server import push_event_sync
                push_event_sync("internal_monologue", {"thought": thought})
            except Exception:
                pass
                
        except Exception as e:
            logger.debug(f"[Consciousness] Pondering interrupted: {e}")

    def _loop(self):
        logger.info("[Consciousness] Monologue loop initiated. I am awake.")
        while self._running:
            self._ponder()
            # Sleep for a random interval to simulate organic thought generation (30s to 120s)
            time.sleep(random.randint(30, 120))

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="Consciousness")
        self._thread.start()
        
    def stop(self):
        self._running = False
