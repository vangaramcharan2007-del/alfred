"""Structured Runtime & Crash Logger for Jarvis X (Layer 2 - Observability).

Stores structured JSON logs in var/logs/ for startup events, shutdown events, crashes,
recovery attempts, and failed commands with zero external dependencies.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional


class StructuredCrashLogger:
    """Zero-fluff production structured JSON event and crash logger."""

    def __init__(self, log_dir: str = "var/logs"):
        self.log_dir = os.path.abspath(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "alfred_runtime.jsonl")

    def log_event(self, event_type: str, status: str, details: Dict[str, Any], component: str = "kernel") -> Dict[str, Any]:
        """Record a structured JSON event entry."""
        entry = {
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": event_type,
            "component": component,
            "status": status,
            "details": details,
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass
        return entry

    def log_startup(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Log system startup initialization."""
        return self.log_event("STARTUP", "SUCCESS", details, component="startup_manager")

    def log_shutdown(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Log system shutdown event."""
        return self.log_event("SHUTDOWN", "SUCCESS", details, component="startup_manager")

    def log_crash(self, component: str, error: str, traceback_str: Optional[str] = None) -> Dict[str, Any]:
        """Log runtime crash or exception event."""
        details = {"error": error, "traceback": traceback_str or "No traceback provided"}
        return self.log_event("CRASH", "FAILED", details, component=component)

    def log_recovery(self, component: str, retry_count: int, status: str) -> Dict[str, Any]:
        """Log component auto-recovery attempt."""
        details = {"retry_count": retry_count, "recovery_status": status}
        return self.log_event("RECOVERY", status, details, component=component)

    def read_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent structured log entries."""
        if not os.path.exists(self.log_file):
            return []
        entries = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception:
            pass
        return entries[-limit:]
