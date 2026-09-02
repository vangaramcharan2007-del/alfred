"""
Active REM Sleep — Idle Memory Consolidation.
Detects user absence and runs background LLM tasks to synthesize 
daily memories into optimized core directives.
"""
import logging
import threading
import time
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class REMSleepEngine:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.idle_threshold_seconds = 1800 # 30 mins
        self._is_sleeping = False
        
    def _get_idle_time(self) -> int:
        """Get Windows system idle time using ctypes."""
        try:
            import ctypes
            import struct
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
            return millis // 1000
        except Exception:
            return 0 # Mock if not on Windows

    def _enter_rem_sleep(self):
        """Consolidate RAG memory into core directives."""
        if self._is_sleeping: return
        self._is_sleeping = True
        logger.info("[REM Sleep] User absent. Entering REM Sleep memory consolidation...")
        
        try:
            from jarvisx.memory.vector_memory import VectorMemory
            import ollama
            
            vm = VectorMemory("alfred_rag_memory")
            recent_memories = "\n".join([r["text"] for r in vm.records[-20:]])
            
            if not recent_memories:
                logger.info("[REM Sleep] No recent memories to consolidate.")
                return
                
            prompt = f"Analyze these recent interactions and extract 3 core preferences or facts about the user's workflow:\n{recent_memories}"
            
            res = ollama.chat(
                model="qwen2.5-coder:1.5b", 
                messages=[{"role": "user", "content": prompt}]
            )
            
            directives_path = Path("var/db/core_directives.md")
            directives_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(directives_path, 'a', encoding='utf-8') as f:
                f.write(f"\n### Dream Log - {time.ctime()}\n{res['message']['content']}\n")
                
            logger.info("[REM Sleep] Consolidation complete. Extracted new core directives.")
        except Exception as e:
            logger.error(f"[REM Sleep] Dream sequence failed: {e}")

    def _loop(self):
        while self._running:
            idle_sec = self._get_idle_time()
            # For demo purposes, if idle > 5 secs, simulate sleep
            if idle_sec > 5 and not self._is_sleeping:
                self._enter_rem_sleep()
            elif idle_sec < 5 and self._is_sleeping:
                logger.info("[REM Sleep] User returned. Waking up.")
                self._is_sleeping = False
                
            time.sleep(2)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="REMSleep")
        self._thread.start()
        
    def stop(self):
        self._running = False
