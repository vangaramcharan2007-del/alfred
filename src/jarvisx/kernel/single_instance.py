"""
Single Instance Guard for Jarvis X / Alfred OS.
Ensures only one instance of any core daemon/service runs at a time.
Automatically terminates stale, orphaned instances to prevent CPU overheating and RAM bloat.
"""

from __future__ import annotations

import atexit
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import psutil

logger = logging.getLogger("jarvisx.single_instance")


class SingleInstanceGuard:
    """Process-level lock using PID files with automatic stale process eviction."""

    def __init__(self, app_name: str, runtime_dir: Optional[Path] = None):
        self.app_name = app_name
        self.runtime_dir = runtime_dir or (Path(__file__).resolve().parent.parent.parent.parent / "var" / "runtime")
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.pid_file = self.runtime_dir / f"{self.app_name}.pid"
        self._acquired = False

    def acquire(self, auto_terminate_stale: bool = True) -> bool:
        """
        Attempts to acquire the single-instance lock.
        If an old instance exists:
        - If auto_terminate_stale is True, cleanly terminates the old process and acquires lock.
        - Otherwise returns False.
        """
        current_pid = os.getpid()

        if self.pid_file.exists():
            try:
                raw = self.pid_file.read_text(encoding="utf-8").strip()
                if raw.isdigit():
                    old_pid = int(raw)
                    if old_pid != current_pid and psutil.pid_exists(old_pid):
                        try:
                            old_proc = psutil.Process(old_pid)
                            proc_name = old_proc.name().lower()
                            if "python" in proc_name:
                                if auto_terminate_stale:
                                    logger.warning(
                                        f"[{self.app_name}] Found existing instance PID {old_pid}. "
                                        f"Terminating stale instance to reclaim CPU/RAM..."
                                    )
                                    old_proc.terminate()
                                    try:
                                        old_proc.wait(timeout=3)
                                    except psutil.TimeoutExpired:
                                        old_proc.kill()
                                    logger.info(f"[{self.app_name}] Successfully terminated stale PID {old_pid}.")
                                else:
                                    logger.error(
                                        f"[{self.app_name}] Another instance is already active (PID {old_pid}). Exiting."
                                    )
                                    return False
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
            except Exception as e:
                logger.debug(f"[{self.app_name}] Error reading stale PID file: {e}")

        # Write our current PID
        try:
            self.pid_file.write_text(str(current_pid), encoding="utf-8")
            self._acquired = True
            atexit.register(self.release)
            logger.info(f"[{self.app_name}] Single-instance lock acquired (PID {current_pid}).")
            return True
        except Exception as e:
            logger.error(f"[{self.app_name}] Failed to write PID file {self.pid_file}: {e}")
            return False

    def release(self):
        """Releases lock by removing the PID file."""
        if not self._acquired:
            return
        try:
            if self.pid_file.exists():
                raw = self.pid_file.read_text(encoding="utf-8").strip()
                if raw == str(os.getpid()):
                    self.pid_file.unlink(missing_ok=True)
            self._acquired = False
            logger.info(f"[{self.app_name}] Single-instance lock released.")
        except Exception:
            pass


def ensure_single_instance(app_name: str) -> SingleInstanceGuard:
    """Convenience helper to enforce single instance in any entry point."""
    guard = SingleInstanceGuard(app_name)
    if not guard.acquire(auto_terminate_stale=True):
        sys.exit(0)
    return guard
