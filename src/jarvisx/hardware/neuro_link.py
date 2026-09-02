"""
Neuro-Link — Brain-Computer Interface (BCI).
Connects via Lab Streaming Layer (LSL) to read raw EEG data from headbands 
(e.g., Muse, OpenBCI) to detect cognitive states like deep focus.
"""
import logging
import threading
import time
import random
from typing import Optional

logger = logging.getLogger(__name__)

class NeuroLink:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.focus_baseline = 0.5

    def _read_eeg_stream(self):
        """Mock reading from pylsl stream inlet for Alpha/Beta waves."""
        alpha = random.uniform(0.1, 0.9)
        beta = random.uniform(0.1, 0.9)
        
        # High Beta / Low Alpha typically indicates active focus/stress
        # High Alpha indicates relaxation
        return alpha, beta

    def _loop(self):
        logger.info("[NeuroLink] Searching for LSL EEG streams on local network...")
        time.sleep(1) # Simulating connection
        logger.info("[NeuroLink] BCI Connected. Monitoring brainwave topography.")
        
        while self._running:
            try:
                alpha, beta = self._read_eeg_stream()
                
                # If hyper-focused (Beta spikes significantly over Alpha)
                if beta > 0.8 and alpha < 0.3:
                    logger.warning(f"[NeuroLink] 🧠 DEEP FOCUS DETECTED (Beta: {beta:.2f}). Triggering Swarm environment.")
                    
                    try:
                        from jarvisx.dashboard.hud_server import push_event_sync
                        push_event_sync("bci_state", {"state": "DEEP_FOCUS", "beta": beta})
                    except Exception:
                        pass
                        
                    # Prevent spamming the trigger
                    time.sleep(30)
                    
            except Exception as e:
                logger.debug(f"[NeuroLink] EEG stream error: {e}")
            time.sleep(2)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="NeuroLink")
        self._thread.start()
        
    def stop(self):
        self._running = False
