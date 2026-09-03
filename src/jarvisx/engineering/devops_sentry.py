import logging
import threading
import time
import psutil

logger = logging.getLogger(__name__)

class DevOpsSentry:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._thread = None
        self._running = False

    def _push_to_ui(self, event_type: str, data: dict):
        """Broadcast events to E.V. UI."""
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def start(self):
        if self._running:
            return
            
        logger.info("[DevOpsSentry] Initializing Runaway Process Guardian...")
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while self._running:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    # Check CPU usage (psutil cpu_percent requires a delay, so we just check instantaneous if available,
                    # or we do a pass over all processes)
                    pass
                    
                # To get accurate cpu_percent per process without blocking the whole loop,
                # we need to track processes over time. A simpler approach:
                # Find any process taking > 80% CPU
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        cpu = proc.cpu_percent(interval=0.1)
                        if cpu > 80.0 and proc.info['name'] not in ["System Idle Process", "System"]:
                            logger.warning(f"[DevOpsSentry] Runaway process detected: {proc.info['name']} (PID: {proc.info['pid']}) using {cpu}% CPU")
                            self._push_to_ui("devops_event", {
                                "action": "runaway_process", 
                                "process": proc.info['name'], 
                                "cpu": cpu
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                        
            except Exception as e:
                logger.debug(f"[DevOpsSentry] Scan error: {e}")
                
            time.sleep(30)
