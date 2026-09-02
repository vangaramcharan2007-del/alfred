"""
Bio-Sync Engine — Cognitive Adaptation.
Simulates reading biometric health data (heart rate, fatigue) and intercepts 
the environment to adjust OS behavior via ContextModeSwitcher.
"""
import logging
import threading
import time
import random
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BioSyncEngine:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.fatigue_level = 0.0 # 0.0 (fresh) to 1.0 (exhausted)
        self.heart_rate = 70
        
    def _poll_biometrics(self):
        """Simulate polling a local API or webcam for health data."""
        # E.g. connect to Apple Health export, Oura Ring API, or webcam PPG.
        self.heart_rate = random.randint(60, 100)
        
        # Simulate gradual fatigue increase over time
        self.fatigue_level += random.uniform(0.01, 0.05)
        if self.fatigue_level > 1.0: self.fatigue_level = 1.0
            
        logger.debug(f"[BioSync] HR: {self.heart_rate}bpm | Fatigue: {self.fatigue_level:.2f}")
        return self.fatigue_level, self.heart_rate

    def _loop(self):
        logger.info("[BioSync] Connected to biometric sensors. Monitoring cognitive load.")
        while self._running:
            try:
                fatigue, hr = self._poll_biometrics()
                
                if fatigue > 0.8:
                    logger.warning("[BioSync] High fatigue detected! Intercepting environment.")
                    try:
                        from jarvisx.dashboard.hud_server import push_event_sync
                        push_event_sync("bio_alert", {
                            "message": "High cognitive load detected. Dimming screens and suppressing notifications.",
                            "fatigue": fatigue,
                            "hr": hr
                        })
                        
                        # In reality: trigger Windows night light, lower volume, pause non-critical tasks
                        import ctypes
                        # Example Windows API call to dim screen or change mode (mocked)
                        # ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
                        
                        # Reset fatigue to simulate resting
                        self.fatigue_level = 0.0
                    except Exception as e:
                        logger.error(f"[BioSync] Environment intercept failed: {e}")
                        
                time.sleep(30) # Poll every 30s
            except Exception as e:
                logger.error(f"[BioSync] Loop error: {e}")
                time.sleep(5)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="BioSync")
        self._thread.start()
        
    def stop(self):
        self._running = False
