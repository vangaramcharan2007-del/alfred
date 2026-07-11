from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class HealthStatus:
    name: str
    healthy: bool
    message: str

    @classmethod
    def ok(cls, message: str = "ok") -> "HealthStatus":
        return cls(name="", healthy=True, message=message)

    @classmethod
    def fail(cls, message: str) -> "HealthStatus":
        return cls(name="", healthy=False, message=message)


class HealthMonitor:
    def __init__(self) -> None:
        self._checks: dict[str, Callable[[], HealthStatus]] = {}

    def register(self, name: str, check: Callable[[], HealthStatus]) -> None:
        self._checks[name] = check

    def run_all(self) -> dict[str, HealthStatus]:
        results: dict[str, HealthStatus] = {}
        for name, check in self._checks.items():
            try:
                status = check()
            except Exception as exc:  # pragma: no cover - defensive boundary
                status = HealthStatus.fail(str(exc))
            results[name] = HealthStatus(name=name, healthy=status.healthy, message=status.message)
        return results
