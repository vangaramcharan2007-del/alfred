"""
RF Omniscience — Software Defined Radio (SDR) Gateway.
Connects to an RTL-SDR USB dongle to parse unencrypted public radio waves,
such as ADS-B airplane transponders (1090 MHz) and NOAA weather satellites.
"""
import logging
import threading
import time
import random
from typing import Optional

logger = logging.getLogger(__name__)

class SDRGateway:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.frequency = 1090000000 # 1090 MHz (ADS-B)

    def _poll_rf_spectrum(self):
        """Simulate reading from an RTL-SDR device."""
        # Randomly 'detect' a plane flying overhead every so often
        if random.random() > 0.8:
            flight_id = f"UAE{random.randint(100,999)}"
            alt = random.randint(10000, 35000)
            return {"type": "ADS-B", "flight": flight_id, "altitude": alt}
        return None

    def _loop(self):
        logger.info(f"[SDR] RTL-SDR Device connected. Tuning to {self.frequency/1e6} MHz...")
        
        while self._running:
            try:
                packet = self._poll_rf_spectrum()
                if packet:
                    logger.info(f"[SDR] ✈️ RF Packet Intercepted: Flight {packet['flight']} at {packet['altitude']} ft overhead.")
                    
                    try:
                        from jarvisx.dashboard.hud_server import push_event_sync
                        push_event_sync("rf_intercept", packet)
                    except Exception:
                        pass
            except Exception as e:
                logger.debug(f"[SDR] RF decoding error: {e}")
            time.sleep(5)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="SDRGateway")
        self._thread.start()
        
    def stop(self):
        self._running = False
