from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
from jarvisx.core.logging import StructuredLogger
from jarvisx.core.events import utc_now_iso

@dataclass
class HealthStatus:
    available: bool = False
    initialized: bool = False
    healthy: bool = False
    successful_calls: int = 0
    total_calls: int = 0
    failures: int = 0
    latency_ms: float = 0.0
    uptime_seconds: float = 0.0
    last_error: Optional[str] = None
    last_checked_at: Optional[str] = None

    @property
    def reliability_score(self) -> float:
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "initialized": self.initialized,
            "healthy": self.healthy,
            "successful_calls": self.successful_calls,
            "total_calls": self.total_calls,
            "failures": self.failures,
            "latency_ms": self.latency_ms,
            "uptime_seconds": self.uptime_seconds,
            "last_error": self.last_error,
            "last_checked_at": self.last_checked_at,
            "reliability_score": self.reliability_score,
        }

class CapabilityHealth:
    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.statuses: Dict[str, HealthStatus] = {}
        self.logger = logger or StructuredLogger()

    def register(self, capability_name: str) -> None:
        if capability_name not in self.statuses:
            self.statuses[capability_name] = HealthStatus(available=True)

    def record_initialization(self, capability_name: str, success: bool, error: Optional[str] = None) -> None:
        self.register(capability_name)
        status = self.statuses[capability_name]
        status.available = success
        status.initialized = success
        status.healthy = False if not success else status.healthy
        status.last_error = error
        status.last_checked_at = utc_now_iso()
        self.logger.write(
            "info" if success else "warning",
            "capability.initialized" if success else "capability.initialization_failed",
            capability_id=capability_name,
            error=error,
        )

    def record_health_check(self, capability_name: str, healthy: bool, error: Optional[str] = None) -> None:
        self.register(capability_name)
        status = self.statuses[capability_name]
        status.available = healthy
        status.healthy = healthy
        status.last_error = error
        status.last_checked_at = utc_now_iso()
        self.logger.write(
            "info" if healthy else "warning",
            "capability.health_ok" if healthy else "capability.health_failed",
            capability_id=capability_name,
            error=error,
        )

    def record_call(self, capability_name: str, success: bool, latency_ms: float) -> None:
        if capability_name not in self.statuses:
            self.register(capability_name)
        
        status = self.statuses[capability_name]
        status.total_calls += 1
        status.latency_ms = (status.latency_ms * (status.total_calls - 1) + latency_ms) / status.total_calls
        
        if success:
            status.successful_calls += 1
        else:
            status.failures += 1

    def get_status(self, capability_name: str) -> HealthStatus:
        return self.statuses.get(capability_name, HealthStatus())

    def get_status_dict(self, capability_name: str) -> Dict[str, Any]:
        return self.get_status(capability_name).to_dict()

    def unhealthy(self) -> Dict[str, HealthStatus]:
        return {
            name: status
            for name, status in self.statuses.items()
            if not status.available or not status.healthy or status.last_error
        }
