from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class HealthStatus:
    name: str
    healthy: bool
    message: str
    latency_ms: float = 0.0

    @classmethod
    def ok(cls, message: str = "ok", latency_ms: float = 0.0) -> "HealthStatus":
        return cls(name="", healthy=True, message=message, latency_ms=latency_ms)

    @classmethod
    def fail(cls, message: str, latency_ms: float = 0.0) -> "HealthStatus":
        return cls(name="", healthy=False, message=message, latency_ms=latency_ms)


class HealthMonitor:
    def __init__(self) -> None:
        self._checks: dict[str, Callable[[], HealthStatus]] = {}

    def register(self, name: str, check: Callable[[], HealthStatus]) -> None:
        self._checks[name] = check

    def run_all(self) -> dict[str, HealthStatus]:
        import time
        results: dict[str, HealthStatus] = {}
        for name, check in self._checks.items():
            start_t = time.time()
            try:
                status = check()
            except Exception as exc:  # pragma: no cover - defensive boundary
                status = HealthStatus.fail(str(exc))
            latency = (time.time() - start_t) * 1000.0
            
            # If the check didn't provide its own latency, use the measured one
            final_latency = status.latency_ms if status.latency_ms > 0 else latency
            results[name] = HealthStatus(name=name, healthy=status.healthy, message=status.message, latency_ms=final_latency)
        return results
