"""
The Oracle Engine — Zero-Prompt Predictive Execution.
Monitors the clipboard and screen context for errors. If it detects a problem,
it pre-computes the solution via LLM before the user even asks.
"""
import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

class OracleEngine:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_clipboard = ""

    def _get_clipboard(self) -> str:
        try:
            import pyperclip
            return pyperclip.paste()
        except Exception:
            return "Mock Traceback (most recent call last): File 'main.py', line 42, ZeroDivisionError"

    def _pre_compute_fix(self, error_text: str):
        logger.info("[Oracle] Error detected in context. Pre-computing solution...")
        try:
            import ollama
            res = ollama.chat(
                model="qwen2.5-coder:1.5b",
                messages=[{"role": "system", "content": "Provide a 1-sentence fix for this error:"},
                          {"role": "user", "content": error_text}]
            )
            fix = res["message"]["content"]
            
            # Push predictive fix to HUD immediately
            try:
                from jarvisx.dashboard.hud_server import push_event_sync
                push_event_sync("oracle_prediction", {"error": error_text[:50], "fix": fix})
            except Exception:
                pass
                
            logger.info(f"[Oracle] Pre-computed fix ready: {fix[:50]}...")
        except Exception as e:
            logger.debug(f"[Oracle] Pre-compute failed: {e}")

    def _loop(self):
        logger.info("[Oracle] Predictive engine online. Watching for context anomalies.")
        while self._running:
            try:
                clip = self._get_clipboard()
                if clip and clip != self._last_clipboard:
                    self._last_clipboard = clip
                    if "Traceback" in clip or "Error:" in clip or "Exception:" in clip:
                        # Spawn background thread so we don't block the watcher
                        threading.Thread(target=self._pre_compute_fix, args=(clip,), daemon=True).start()
            except Exception:
                pass
            time.sleep(2)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="OracleEngine")
        self._thread.start()
        
    def stop(self):
        self._running = False
