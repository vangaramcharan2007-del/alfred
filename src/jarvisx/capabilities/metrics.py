from __future__ import annotations
from dataclasses import dataclass

@dataclass
class CapabilityMetrics:
    capability_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_latency_ms: float = 0.0
    fallback_count: int = 0

    @property
    def success_rate(self) -> float:
        if self.capability_calls == 0:
            return 1.0
        return self.successful_calls / self.capability_calls

    @property
    def failure_rate(self) -> float:
        if self.capability_calls == 0:
            return 0.0
        return self.failed_calls / self.capability_calls

    @property
    def average_latency(self) -> float:
        if self.capability_calls == 0:
            return 0.0
        return self.total_latency_ms / self.capability_calls
