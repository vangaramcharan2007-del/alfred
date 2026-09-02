"""Data Models for Phase 98: Reliability Kernel & Production Hardening."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RecoveryAction(str, Enum):
    SOFT_RESTART = "SOFT_RESTART"
    CLEAR_CACHE = "CLEAR_CACHE"
    RELOAD_PROVIDER = "RELOAD_PROVIDER"
    RESTORE_BACKUP = "RESTORE_BACKUP"
    SAFE_MODE = "SAFE_MODE"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"


class RecoveryState(str, Enum):
    RUNNING = "RUNNING"
    FAILURE_DETECTED = "FAILURE_DETECTED"
    DIAGNOSING = "DIAGNOSING"
    SOFT_RESET = "SOFT_RESET"
    SAFE_MODE = "SAFE_MODE"


@dataclass
class HealthState:
    status: str  # HEALTHY, DEGRADED, UNHEALTHY
    memory_rss_mb: float
    cpu_percent: float
    active_threads: int
    uptime_seconds: float
    database_status: Dict[str, str]  # db_name -> status
    latency_ms: float
    queue_depth: int
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "memory_rss_mb": round(self.memory_rss_mb, 2),
            "cpu_percent": round(self.cpu_percent, 1),
            "active_threads": self.active_threads,
            "uptime_seconds": round(self.uptime_seconds, 1),
            "database_status": self.database_status,
            "latency_ms": round(self.latency_ms, 2),
            "queue_depth": self.queue_depth,
            "last_error": self.last_error,
        }


@dataclass
class CrashEvent:
    id: str
    timestamp: float
    component: str
    exception_type: str
    stack_trace: str
    recovery_action: RecoveryAction

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "component": self.component,
            "exception_type": self.exception_type,
            "stack_trace": self.stack_trace,
            "recovery_action": self.recovery_action.value,
        }


@dataclass
class BackupSnapshot:
    id: str
    timestamp: float
    snapshot_dir: str
    checksum_manifest: Dict[str, str]  # filename -> sha256
    size_bytes: int
    status: str  # VERIFIED, CORRUPTED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "snapshot_dir": self.snapshot_dir,
            "checksum_manifest": self.checksum_manifest,
            "size_bytes": self.size_bytes,
            "status": self.status,
        }


@dataclass
class EvolutionEvent:
    id: str
    timestamp: float
    component: str
    old_behavior: str
    new_behavior: str
    reason: str
    validation_result: str
    impact_delta: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "component": self.component,
            "old_behavior": self.old_behavior,
            "new_behavior": self.new_behavior,
            "reason": self.reason,
            "validation_result": self.validation_result,
            "impact_delta": self.impact_delta,
        }
