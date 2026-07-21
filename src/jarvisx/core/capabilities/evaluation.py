from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ProviderStatus(Enum):
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    OFFLINE = "Offline"
    UNAVAILABLE = "Unavailable"


@dataclass
class ProviderHealth:
    """Tracks the health and success metrics of a provider for runtime learning."""
    status: ProviderStatus = ProviderStatus.HEALTHY
    last_success: float = 0.0
    last_failure: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    total_latency_ms: float = 0.0
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0 # Assume perfect until proven otherwise
        return self.success_count / total
        
    @property
    def average_latency_ms(self) -> float:
        if self.success_count == 0:
            return 0.0
        return self.total_latency_ms / self.success_count

    def record_success(self, latency_ms: float = 0.0):
        self.success_count += 1
        self.last_success = time.time()
        self.total_latency_ms += latency_ms
        if self.status != ProviderStatus.HEALTHY and self.success_rate > 0.8:
            self.status = ProviderStatus.HEALTHY

    def record_failure(self):
        self.failure_count += 1
        self.last_failure = time.time()
        if self.success_rate < 0.5:
            self.status = ProviderStatus.DEGRADED
        if self.failure_count > 10 and self.success_rate < 0.1:
            self.status = ProviderStatus.OFFLINE


@dataclass
class ProviderEvaluation:
    """The result of a provider evaluating its fitness for a specific task."""
    provider_name: str
    capability: str
    
    score: float = 0.0
    available: bool = False
    confidence: float = 0.0
    latency_ms: float = 0.0
    estimated_cost: float = 0.0
    supports_streaming: bool = False
    requires_network: bool = False
    reason: str = "Uninitialized"
    
    # Injected by the runtime automatically based on the provider's historical health
    health_status: ProviderStatus = ProviderStatus.HEALTHY
    success_rate: float = 1.0
