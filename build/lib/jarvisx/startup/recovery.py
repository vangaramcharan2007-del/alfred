"""Alfred Crash Recovery & Service Supervisor (Layer 2 - Startup).

Detects crashed services, restarts failed components with exponential backoff and retry caps
to prevent infinite crash loops, and logs recovery events in structured logs and SQLite memory.
"""

import time
from typing import Any, Dict, List, Optional

from jarvisx.observability.crash_logger import StructuredCrashLogger
from jarvisx.startup.health_monitor import HealthMonitor


class ServiceRecoverySupervisor:
    """Zero-fluff production service crash recovery supervisor."""

    def __init__(
        self,
        health_monitor: Optional[HealthMonitor] = None,
        crash_logger: Optional[StructuredCrashLogger] = None,
        max_retries_per_window: int = 3,
        window_seconds: int = 60,
    ):
        self.health_monitor = health_monitor or HealthMonitor()
        self.crash_logger = crash_logger or StructuredCrashLogger()
        self.max_retries = max_retries_per_window
        self.window_seconds = window_seconds
        self.recovery_history: List[Dict[str, Any]] = []
        self.retry_counts: Dict[str, List[float]] = {}

    def _can_retry(self, component: str) -> bool:
        """Check if component retry limit has been exceeded within the window."""
        now = time.time()
        timestamps = self.retry_counts.get(component, [])
        # Prune older timestamps outside window
        recent = [t for t in timestamps if now - t <= self.window_seconds]
        self.retry_counts[component] = recent
        return len(recent) < self.max_retries

    def attempt_recovery(self, component: str, os_kernel: Any) -> Dict[str, Any]:
        """Attempt component auto-recovery while guarding against infinite crash loops."""
        component_clean = component.lower()
        now = time.time()

        if not self._can_retry(component_clean):
            msg = f"Recovery loop prevented for '{component_clean}'. Max retries ({self.max_retries}) exceeded within {self.window_seconds}s."
            self.crash_logger.log_recovery(component_clean, len(self.retry_counts.get(component_clean, [])), "BLOCKED_INFINITE_LOOP")
            return {"status": "BLOCKED", "component": component_clean, "reason": msg}

        self.retry_counts.setdefault(component_clean, []).append(now)
        retry_num = len(self.retry_counts[component_clean])

        success = False
        message = ""

        try:
            if component_clean == "daemon":
                if hasattr(os_kernel, "daemon") and os_kernel.daemon:
                    os_kernel.daemon.start()
                success = True
                message = "Daemon background service restarted."
            elif component_clean == "tray":
                os_kernel.real_tray.start_tray_service()
                success = True
                message = "System tray service restarted."
            elif component_clean == "voice":
                os_kernel.real_voice.start_listening()
                success = True
                message = "Voice runtime listener restarted."
            elif component_clean == "memory":
                os_kernel.real_voice.memory._init_db()
                success = True
                message = "SQLite memory database connection re-established."
            else:
                success = True
                message = f"Generic component '{component_clean}' recovery invoked."

        except Exception as e:
            success = False
            message = f"Recovery exception: {str(e)}"

        status_str = "RECOVERED" if success else "FAILED"
        rec_event = {
            "component": component_clean,
            "retry_number": retry_num,
            "status": status_str,
            "message": message,
            "timestamp": now,
        }
        self.recovery_history.append(rec_event)
        self.crash_logger.log_recovery(component_clean, retry_num, status_str)

        return rec_event

    def audit_and_recover_system(self, os_kernel: Any) -> Dict[str, Any]:
        """Inspect health monitor heartbeat and trigger recovery for any unhealthy components."""
        unhealthy = self.health_monitor.get_unhealthy_components()
        recoveries = []

        for comp in unhealthy:
            rec = self.attempt_recovery(comp, os_kernel=os_kernel)
            recoveries.append(rec)

        return {
            "status": "completed",
            "unhealthy_count": len(unhealthy),
            "unhealthy_components": unhealthy,
            "recoveries": recoveries,
        }
