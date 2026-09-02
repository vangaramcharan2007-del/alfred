from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.kernel.subsystem_manager import SubsystemManager

class LifecycleManager:
    def __init__(self, subsystem_manager: Optional[SubsystemManager] = None):
        self.subsystem_mgr = subsystem_manager or SubsystemManager()
        self.boot_start: float = 0.0
        self.boot_end: float = 0.0
        self.state: str = "STOPPED"  # STOPPED, BOOTING, RUNNING, SHUTTING_DOWN

    async def boot_all(self) -> Dict[str, Any]:
        self.state = "BOOTING"
        self.boot_start = time.time()

        for name in list(self.subsystem_mgr.subsystems.keys()):
            self.subsystem_mgr.boot_subsystem(name)
            self.subsystem_mgr.online_subsystem(name)

        self.boot_end = time.time()
        self.state = "RUNNING"

        return {
            "state": self.state,
            "boot_duration": round(self.boot_end - self.boot_start, 3),
            "subsystems_online": len(self.subsystem_mgr.subsystems),
            "all_healthy": self.subsystem_mgr.all_online()
        }

    async def shutdown_all(self) -> Dict[str, Any]:
        self.state = "SHUTTING_DOWN"
        for name in list(self.subsystem_mgr.subsystems.keys()):
            self.subsystem_mgr.set_status(name, "OFFLINE")
        self.state = "STOPPED"
        return {"state": self.state}

    def get_runtime_info(self) -> Dict[str, Any]:
        uptime = time.time() - self.boot_start if self.boot_start > 0 else 0.0
        return {
            "state": self.state,
            "uptime_seconds": round(uptime, 2),
            "degraded": self.subsystem_mgr.get_degraded()
        }
