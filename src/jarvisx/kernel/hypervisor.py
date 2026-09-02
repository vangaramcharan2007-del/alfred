"""
The Hypervisor — OS Resource Governor.
Manages the CPU, RAM, and GPU/VRAM load of the Jarvis X ecosystem.
Queues LLM requests, dynamically sleeps/wakes modules based on hardware load,
and prevents Python GIL choke.
"""
import logging
import threading
import time
import psutil
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class LLMQueue:
    """A global lock to prevent concurrent Ollama requests from exhausting VRAM."""
    def __init__(self):
        self._lock = threading.Lock()
        
    def execute(self, func, *args, **kwargs):
        with self._lock:
            # Yield to other threads slightly before locking VRAM
            time.sleep(0.1)
            return func(*args, **kwargs)

class Hypervisor:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.llm_queue = LLMQueue()
        self._running = False
        self._thread = None
        self._managed_modules = {}
        
        self.MAX_CPU_PERCENT = 85.0
        self.MAX_RAM_PERCENT = 90.0

    def register_module(self, name: str, module_instance, priority: str = "low"):
        """Register a module to be governed. Priority: 'critical', 'normal', 'low'."""
        self._managed_modules[name] = {
            "instance": module_instance,
            "priority": priority,
            "status": "sleeping"
        }
        logger.info(f"[Hypervisor] Registered module: {name} ({priority} priority)")

    def _govern_resources(self):
        logger.info("[Hypervisor] Resource Governor ONLINE. Monitoring system thermals and compute.")
        
        while self._running:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            
            # If system is choking, suspend low-priority modules
            if cpu > self.MAX_CPU_PERCENT or ram > self.MAX_RAM_PERCENT:
                logger.warning(f"[Hypervisor] CRITICAL LOAD (CPU: {cpu}%, RAM: {ram}%). Initiating load shedding...")
                for name, meta in self._managed_modules.items():
                    if meta["priority"] == "low" and meta["status"] == "running":
                        try:
                            meta["instance"].stop()
                            meta["status"] = "suspended"
                            logger.info(f"[Hypervisor] Suspended {name} to save resources.")
                        except Exception:
                            pass
            
            # If system is healthy, wake up suspended modules
            elif cpu < 50.0 and ram < 75.0:
                for name, meta in self._managed_modules.items():
                    if meta["status"] in ["suspended", "sleeping"]:
                        try:
                            meta["instance"].start()
                            meta["status"] = "running"
                            logger.info(f"[Hypervisor] Booted {name}.")
                        except Exception:
                            pass
                            
            time.sleep(5)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._govern_resources, daemon=True, name="Hypervisor")
        self._thread.start()
        
    def stop(self):
        self._running = False
