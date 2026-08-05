from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ServiceState:
    name: str
    status: str = "OFFLINE"  # ONLINE, OFFLINE, DEGRADED, FAILED
    details: Dict[str, Any] = field(default_factory=dict)
    updated_at: float = field(default_factory=time.time)

class RuntimeState:
    def __init__(self):
        self.state_name: str = "STOPPED"  # STOPPED, BOOTING, RUNNING, SHUTTING_DOWN
        self.services: Dict[str, ServiceState] = {}
        self.start_time: float = 0.0

    def set_service(self, name: str, status: str, details: Optional[Dict[str, Any]] = None) -> ServiceState:
        s = ServiceState(name=name, status=status, details=details or {}, updated_at=time.time())
        self.services[name] = s
        return s

    def is_all_online(self) -> bool:
        return all(s.status == "ONLINE" for s in self.services.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state_name,
            "uptime_seconds": round(time.time() - self.start_time, 2) if self.start_time > 0 else 0.0,
            "services": {k: {"status": v.status, "details": v.details} for k, v in self.services.items()}
        }

    def generate_startup_banner(self) -> str:
        lines = [
            "=========================",
            "       JARVIS X",
            "=========================",
            ""
        ]
        for srv in ["Memory", "LLM", "Voice", "Vision", "Git", "Agents"]:
            status = self.services.get(srv, ServiceState(srv, "OFFLINE")).status
            lines.append(f"{srv:<12} ........ {status}")
        lines.extend([
            "",
            "Alfred online.",
            ""
        ])
        return "\n".join(lines)
