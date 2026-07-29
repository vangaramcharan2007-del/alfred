from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
from jarvisx.core.logging import StructuredLogger

@dataclass
class HealthStatus:
    available: bool = False
    successful_calls: int = 0
    total_calls: int = 0
    failures: int = 0
    latency_ms: float = 0.0
    uptime_seconds: float = 0.0

    @property
    def reliability_score(self) -> float:
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls

class CapabilityHealth:
    def __init__(self):
        self.statuses: Dict[str, HealthStatus] = {}
        self.logger = StructuredLogger()

    def register(self, capability_name: str) -> None:
        if capability_name not in self.statuses:
            self.statuses[capability_name] = HealthStatus(available=True)

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
