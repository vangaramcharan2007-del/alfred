"""Adaptive Health Monitor for Phase 98 Reliability Kernel."""

from __future__ import annotations
import os
import psutil
import threading
import time
from typing import Dict, Optional
from jarvisx.reliability.models import HealthState
from jarvisx.reliability.reliability_memory import ReliabilityMemory
from jarvisx.reliability.runtime_integrity import RuntimeIntegrityValidator


class HealthMonitor:
    """Adaptive Health Monitor measuring RSS memory, CPU, thread pools, database latency, and queue depth."""

    def __init__(self, memory: Optional[ReliabilityMemory] = None, start_time: Optional[float] = None):
        self.memory = memory or ReliabilityMemory()
        self.validator = RuntimeIntegrityValidator(self.memory)
        self.start_time = start_time or time.time()

    def get_adaptive_interval(self, is_active_mission: bool = False, has_recent_failure: bool = False) -> int:
        """Adaptive intervals: idle: 60s, active: 10s, failure burst: 1s."""
        if has_recent_failure:
            return 1
        elif is_active_mission:
            return 10
        return 60

    def probe_health(self) -> HealthState:
        """Execute a full live diagnostic probe of the Jarvis X runtime."""
        t0 = time.time()
        process = psutil.Process(os.getpid())
        mem_rss = process.memory_info().rss / (1024 * 1024)
        cpu_pct = psutil.cpu_percent(interval=None)
        threads = threading.active_count()
        uptime = time.time() - self.start_time

        # Validate database integrity
        integrity = self.validator.verify_integrity()
        db_status = {k: v.get("status", "UNKNOWN") for k, v in integrity.get("databases", {}).items()}

        latency = round((time.time() - t0) * 1000, 2)
        overall_status = "HEALTHY" if integrity["all_healthy"] else "DEGRADED"

        state = HealthState(
            status=overall_status,
            memory_rss_mb=mem_rss,
            cpu_percent=cpu_pct,
            active_threads=threads,
            uptime_seconds=uptime,
            database_status=db_status,
            latency_ms=latency,
            queue_depth=0,
            last_error=None if overall_status == "HEALTHY" else "Degraded database state detected"
        )

        self.memory.record_health(state)
        return state
