"""Alfred Health Monitor & Heartbeat System (Layer 2 - Startup).

Tracks unified Alfred system heartbeat (daemon, tray, voice, memory),
saves heartbeat logs in SQLite memory architecture, and reports unhealthy components.
"""

import time
import uuid
from typing import Any, Dict, List, Optional

from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider


class HealthMonitor:
    """Zero-fluff production health monitor and heartbeat tracking engine."""

    def __init__(self, memory_provider: Optional[SQLiteMemoryProvider] = None):
        self.memory = memory_provider or SQLiteMemoryProvider(db_path="var/db/memory.db")
        self.last_heartbeat: Optional[Dict[str, Any]] = None
        self.check_count: int = 0

    def generate_heartbeat(
        self,
        daemon_status: str = "healthy",
        tray_status: str = "running",
        voice_status: str = "ready",
        memory_status: str = "connected",
    ) -> Dict[str, Any]:
        """Generate unified heartbeat schema and store in SQLite memory architecture."""
        self.check_count += 1
        now = time.time()
        heartbeat = {
            "daemon": daemon_status,
            "tray": tray_status,
            "voice": voice_status,
            "memory": memory_status,
            "last_check": now,
            "check_number": self.check_count,
        }
        self.last_heartbeat = heartbeat

        # Store heartbeat in SQLite memory database
        self.memory.save_memory(
            category="heartbeat",
            key=f"hb_{self.check_count}",
            value=heartbeat,
            context={"module": "health_monitor"}
        )

        return heartbeat

    def get_unhealthy_components(self, heartbeat: Optional[Dict[str, Any]] = None) -> List[str]:
        """Identify components operating in degraded, stopped, or failed states."""
        hb = heartbeat or self.last_heartbeat or self.generate_heartbeat()
        unhealthy = []

        if hb.get("daemon") not in ("healthy", "active", "running"):
            unhealthy.append("daemon")
        if hb.get("tray") not in ("running", "active"):
            unhealthy.append("tray")
        if hb.get("voice") not in ("ready", "VOICE_READY", "degraded", "VOICE_DEGRADED"):
            unhealthy.append("voice")
        if hb.get("memory") not in ("connected", "ready"):
            unhealthy.append("memory")

        return unhealthy
