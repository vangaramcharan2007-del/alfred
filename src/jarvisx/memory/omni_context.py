"""
Omni-Context Timeline — Photographic workflow memory.
Takes lightweight text snapshots of the active window and screen OCR 
to build a searchable timeline of everything you've seen.
"""
import logging
import threading
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class OmniContextTimeline:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._db_path = Path("var/db/omni_timeline.jsonl")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._interval = 10 # seconds

    def _get_active_window(self) -> str:
        try:
            import pygetwindow as gw
            win = gw.getActiveWindow()
            return win.title if win and win.title else "Unknown"
        except Exception:
            return "Unknown"
            
    def _get_screen_text(self) -> str:
        """Simulate lightweight OCR of the screen for context extraction."""
        return "Simulated screen text payload."

    def _snapshot_loop(self):
        logger.info("[OmniContext] Timeline recording started.")
        while self._running:
            try:
                title = self._get_active_window()
                text = self._get_screen_text()
                
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "window": title,
                    "text_preview": text[:100]
                }
                
                with open(self._db_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry) + "\n")
                    
                # Also push to HUD
                try:
                    from jarvisx.dashboard.hud_server import push_event_sync
                    push_event_sync("timeline_snapshot", {"window": title[:40]})
                except Exception:
                    pass
                    
                time.sleep(self._interval)
            except Exception as e:
                logger.debug(f"[OmniContext] Snapshot failed: {e}")
                time.sleep(self._interval)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._snapshot_loop, daemon=True, name="OmniContext")
        self._thread.start()
        
    def stop(self):
        self._running = False
