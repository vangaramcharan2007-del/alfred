from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class SubsystemStatus:
    name: str
    status: str = "OFFLINE"  # OFFLINE, BOOTING, ONLINE, DEGRADED, FAILED
    boot_time: float = 0.0
    last_heartbeat: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "boot_time": round(self.boot_time, 3),
            "last_heartbeat": round(self.last_heartbeat, 3),
            "error": self.error
        }

class SubsystemManager:
    def __init__(self):
        self.subsystems: Dict[str, SubsystemStatus] = {}

    def register_subsystem(self, name: str) -> SubsystemStatus:
        status = SubsystemStatus(name=name)
        self.subsystems[name] = status
        return status

    def set_status(self, name: str, status: str, error: Optional[str] = None) -> None:
        if name in self.subsystems:
            self.subsystems[name].status = status
            self.subsystems[name].last_heartbeat = time.time()
            if error:
                self.subsystems[name].error = error

    def boot_subsystem(self, name: str) -> None:
        if name in self.subsystems:
            self.subsystems[name].status = "BOOTING"
            self.subsystems[name].boot_time = time.time()

    def online_subsystem(self, name: str) -> None:
        if name in self.subsystems:
            self.subsystems[name].status = "ONLINE"
            self.subsystems[name].last_heartbeat = time.time()

    def get_all_statuses(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.subsystems.values()]

    def all_online(self) -> bool:
        return all(s.status == "ONLINE" for s in self.subsystems.values())

    def get_degraded(self) -> List[str]:
        return [n for n, s in self.subsystems.items() if s.status in ("DEGRADED", "FAILED")]

    def recover_subsystem(self, name: str) -> bool:
        if name in self.subsystems:
            self.subsystems[name].status = "ONLINE"
            self.subsystems[name].last_heartbeat = time.time()
            self.subsystems[name].error = None
            return True
        return False

