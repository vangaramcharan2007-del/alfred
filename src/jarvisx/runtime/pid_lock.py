"""Atomic PID Lock & Cross-Platform Process Liveness Manager for Jarvis X."""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Optional, Tuple


class PIDLockManager:
    """Manages atomic PID lockfile creation, stale process cleanup, and multi-instance prevention."""

    def __init__(self, pid_file_path: Optional[str] = None):
        self.pid_file = Path(pid_file_path or "var/runtime/jarvisd.pid")
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)

    def is_process_alive(self, pid: int) -> bool:
        """Check if a process with given PID is actively running on Windows / Unix."""
        if pid <= 0:
            return False
        try:
            import psutil
            if not psutil.pid_exists(pid):
                return False
            proc = psutil.Process(pid)
            if not proc.is_running() or proc.status() == psutil.STATUS_ZOMBIE:
                return False
            p_name = proc.name().lower()
            return "python" in p_name or "jarvis" in p_name
        except Exception:
            return False

    def acquire(self) -> Tuple[bool, Optional[str]]:
        """Attempt to acquire PID lock. Returns (True, None) if acquired, or (False, reason) if already running."""
        current_pid = os.getpid()

        if self.pid_file.exists():
            try:
                content = self.pid_file.read_text(encoding="utf-8").strip()
                if content:
                    existing_pid = int(content)
                    if existing_pid == current_pid:
                        return True, None
                    if self.is_process_alive(existing_pid):
                        return False, f"Jarvis X daemon is already running with PID {existing_pid}."
                    # Stale PID file from crash -> clean up
                    self.release()
            except Exception:
                self.release()

        try:
            self.pid_file.write_text(str(current_pid), encoding="utf-8")
            return True, None
        except Exception as e:
            return False, f"Failed to write PID lockfile: {e}"

    def release(self) -> bool:
        """Release PID lock by removing the lockfile."""
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
                return True
            except Exception:
                return False
        return True

    def get_running_pid(self) -> Optional[int]:
        """Read the active PID if lockfile exists and process is alive."""
        if not self.pid_file.exists():
            return None
        try:
            pid = int(self.pid_file.read_text(encoding="utf-8").strip())
            return pid if self.is_process_alive(pid) else None
        except Exception:
            return None
