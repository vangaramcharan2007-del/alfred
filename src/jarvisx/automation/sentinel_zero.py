import logging
import threading
import time
import psutil

logger = logging.getLogger(__name__)

class SentinelZero:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread = None
        self._known_ports = {80, 443, 8765, 53, 22, 3389}

    def _push_to_ui(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def start(self):
        if self._running:
            return
        self._running = True
        logger.info("[SentinelZero] Cybersecurity SOC online.")
        self._thread = threading.Thread(target=self._loop, daemon=True, name="SentinelZero")
        self._thread.start()

    def _loop(self):
        while self._running:
            try:
                # Scan active network connections
                connections = psutil.net_connections(kind='inet')
                suspicious = []
                for conn in connections:
                    if conn.status == 'ESTABLISHED' and conn.raddr:
                        port = conn.raddr.port
                        if port not in self._known_ports:
                            suspicious.append(f"Port {port} (PID {conn.pid})")
                
                if suspicious:
                    msg = f"Detected {len(suspicious)} unusual outgoing connections. Threat analysis nominal."
                    logger.warning(f"[SentinelZero] {msg}")
                    self._push_to_ui("security_event", {"status": "Anomaly Detected", "details": msg})
            except Exception as e:
                logger.debug(f"[SentinelZero] Loop error: {e}")
                
            time.sleep(300) # Scan every 5 mins
