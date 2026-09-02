"""Production Watchdog & Resource Limit Guard for Jarvis X.

Monitors memory RSS consumption, disk space, rate limits, and watchdog heartbeats.
"""

from __future__ import annotations

import os
import psutil
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResourceLimitGuard:
    """Monitors system resource pressure and enforces safety thresholds."""

    MAX_RSS_MB_DEFAULT = 2048.0  # 2 GB max RSS
    MIN_FREE_DISK_MB = 512.0     # 512 MB min free disk

    def __init__(
        self,
        max_rss_mb: float = MAX_RSS_MB_DEFAULT,
        min_free_disk_mb: float = MIN_FREE_DISK_MB,
        rate_limit_per_minute: int = 60,
    ):
        self.max_rss_mb = max_rss_mb
        self.min_free_disk_mb = min_free_disk_mb
        self.rate_limit_per_minute = rate_limit_per_minute
        self._request_timestamps: list[float] = []

    def check_resources(self) -> Dict[str, Any]:
        """Verify current process RSS memory and available disk space."""
        process = psutil.Process(os.getpid())
        mem_rss_mb = process.memory_info().rss / (1024 * 1024)
        disk_free_mb = psutil.disk_usage(".").free / (1024 * 1024)

        rss_ok = mem_rss_mb <= self.max_rss_mb
        disk_ok = disk_free_mb >= self.min_free_disk_mb

        if not rss_ok:
            logger.warning(f"[WATCHDOG] Memory warning: RSS {mem_rss_mb:.1f} MB exceeds limit {self.max_rss_mb:.1f} MB")
        if not disk_ok:
            logger.warning(f"[WATCHDOG] Disk warning: Free space {disk_free_mb:.1f} MB below {self.min_free_disk_mb:.1f} MB")

        return {
            "healthy": rss_ok and disk_ok,
            "memory_rss_mb": round(mem_rss_mb, 2),
            "memory_limit_mb": self.max_rss_mb,
            "disk_free_mb": round(disk_free_mb, 2),
            "disk_min_mb": self.min_free_disk_mb,
            "rss_ok": rss_ok,
            "disk_ok": disk_ok,
        }

    def check_rate_limit(self) -> bool:
        """Enforce sliding window rate limit per minute."""
        now = time.time()
        self._request_timestamps = [t for t in self._request_timestamps if now - t < 60.0]
        if len(self._request_timestamps) >= self.rate_limit_per_minute:
            return False
        self._request_timestamps.append(now)
        return True
