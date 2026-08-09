"""Runtime State Manager for Jarvis X In-Memory Runtime & Persistent Daemon."""

from __future__ import annotations
import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ServiceState:
    name: str
    status: str = "OFFLINE"  # ONLINE, OFFLINE, DEGRADED, FAILED
    details: Dict[str, Any] = field(default_factory=dict)
    updated_at: float = field(default_factory=time.time)


class RuntimeState:
    """In-memory runtime state for JarvisRuntime."""

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
            "services": {k: {"status": v.status, "details": v.details} for k, v in self.services.items()},
        }

    def generate_startup_banner(self) -> str:
        lines = [
            "=========================",
            "       JARVIS X",
            "=========================",
            "",
        ]
        for srv in ["Memory", "LLM", "Voice", "Vision", "Git", "Agents"]:
            status = self.services.get(srv, ServiceState(srv, "OFFLINE")).status
            lines.append(f"{srv:<12} ........ {status}")
        lines.extend([
            "",
            "Alfred online.",
            "",
        ])
        return "\n".join(lines)


@dataclass
class DaemonRuntimeState:
    """Persistent state for the always-on background daemon."""
    status: str = "OFFLINE"  # STARTING, RUNNING, STOPPING, OFFLINE, DEGRADED
    pid: Optional[int] = None
    started_at: Optional[float] = None
    uptime_seconds: float = 0.0
    active_services: List[str] = field(default_factory=list)
    last_heartbeat: float = 0.0
    last_event: Optional[str] = None
    total_commands_executed: int = 0
    total_events_processed: int = 0
    memory_rss_mb: float = 0.0
    cpu_percent: float = 0.0
    health: str = "GREEN"  # GREEN, YELLOW, RED


class RuntimeStateManager:
    """Persists and inspects real-time daemon state file for CLI queries."""

    def __init__(self, state_file_path: Optional[str] = None):
        self.state_file = Path(state_file_path or "var/runtime/state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._current_state = DaemonRuntimeState()

    def update_state(self, **kwargs) -> DaemonRuntimeState:
        """Update fields on the runtime state and persist to disk."""
        for key, value in kwargs.items():
            if hasattr(self._current_state, key):
                setattr(self._current_state, key, value)

        if self._current_state.started_at:
            self._current_state.uptime_seconds = time.time() - self._current_state.started_at
        self._current_state.last_heartbeat = time.time()

        try:
            self.state_file.write_text(json.dumps(asdict(self._current_state), indent=2), encoding="utf-8")
        except Exception:
            pass

        return self._current_state

    def load_state(self) -> DaemonRuntimeState:
        """Read the persisted state from disk."""
        if not self.state_file.exists():
            return DaemonRuntimeState(status="OFFLINE")

        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            return DaemonRuntimeState(**data)
        except Exception:
            return DaemonRuntimeState(status="OFFLINE")

    def clear(self):
        """Mark daemon as OFFLINE."""
        self.update_state(status="OFFLINE", pid=None, active_services=[])
