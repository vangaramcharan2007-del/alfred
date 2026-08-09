"""Periodic Heartbeat & Health Monitor for Jarvis X Daemon."""

from __future__ import annotations
import os
import threading
import time
from typing import Callable, Optional
from jarvisx.runtime.state import RuntimeStateManager


class DaemonHeartbeatMonitor:
    """Runs a lightweight background thread every interval_seconds to log health and update system metrics."""

    def __init__(
        self,
        state_manager: RuntimeStateManager,
        interval_seconds: float = 30.0,
        on_heartbeat: Optional[Callable[[], None]] = None,
    ):
        self.state_manager = state_manager
        self.interval = interval_seconds
        self.on_heartbeat = on_heartbeat
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start the background heartbeat thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, name="HeartbeatMonitor", daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the heartbeat thread."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _get_process_metrics(self) -> tuple[float, float]:
        """Obtain memory RSS (MB) and CPU usage percentage."""
        rss_mb = 0.0
        cpu_percent = 0.0
        try:
            import psutil
            proc = psutil.Process(os.getpid())
            rss_mb = proc.memory_info().rss / (1024 * 1024)
            cpu_percent = proc.cpu_percent(interval=None)
        except Exception:
            pass
        return rss_mb, cpu_percent

    def _run_loop(self):
        while self._running:
            rss_mb, cpu = self._get_process_metrics()
            self.state_manager.update_state(
                memory_rss_mb=round(rss_mb, 2),
                cpu_percent=round(cpu, 2),
                health="GREEN" if rss_mb < 300.0 else "YELLOW",
            )
            if self.on_heartbeat:
                try:
                    self.on_heartbeat()
                except Exception:
                    pass

            # Sleep in small increments for responsive stop
            for _ in range(int(self.interval * 2)):
                if not self._running:
                    break
                time.sleep(0.5)
