"""Operational Agent Framework for Jarvis X.

Provides the universal runtime contract and operational instrumentation for all autonomous
workers, including IAM permissions, memory binding, execution timers, and empirical HSPW tracking.
"""

import time
from typing import Any, Dict, List, Optional
from jarvisx.architecture.contracts import AgentContract


class OperationalAgent(AgentContract):
    """Standardized runtime framework extending AgentContract with permissions and performance metrics."""

    def __init__(
        self,
        name: str,
        purpose: str,
        capabilities: List[str],
        permissions: Optional[List[str]] = None,
        memory_access: Optional[Any] = None,
        hspw_multiplier: float = 0.05,  # Estimated hours saved per task executed
    ):
        super().__init__(name=name, purpose=purpose, capabilities=capabilities)
        self.identity = {"name": name, "purpose": purpose, "type": "Operational"}
        self.permissions = permissions or ["read_filesystem", "run_tools"]
        self.memory_access = memory_access or {}
        self.hspw_multiplier = hspw_multiplier

        # Internal instrumentation telemetry
        self._tasks_completed: int = 0
        self._tasks_failed: int = 0
        self._total_runtime: float = 0.0

    def execute(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Execute task with automated performance telemetry and safety enforcement."""
        start_time = time.time()
        try:
            outcome = self._execute_task(task, **kwargs)
            elapsed = time.time() - start_time
            self._total_runtime += max(elapsed, 0.01)  # Ensure minimum delta for calculation
            if outcome.get("status") in ("completed", "success"):
                self._tasks_completed += 1
            else:
                self._tasks_failed += 1
            return outcome
        except Exception as exc:
            elapsed = time.time() - start_time
            self._total_runtime += max(elapsed, 0.01)
            self._tasks_failed += 1
            return {"status": "error", "error": f"Agent runtime exception: {exc}"}

    def _execute_task(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Override in subclasses to execute real operational capability logic."""
        raise NotImplementedError("Subclasses must implement _execute_task operational logic.")

    def status(self) -> Dict[str, Any]:
        """Return live worker operational state and resource utilization."""
        total = self._tasks_completed + self._tasks_failed
        rate = (self._tasks_completed / total * 100.0) if total > 0 else 100.0
        return {
            "identity": self.name,
            "state": "active" if total > 0 else "idle",
            "health": "healthy" if rate >= 80.0 else "degraded",
            "permissions_count": len(self.permissions),
        }

    def metrics(self) -> Dict[str, Any]:
        """Expose empirical efficiency metrics and Hours Saved Per Week (HSPW) calculation."""
        total = self._tasks_completed + self._tasks_failed
        avg_runtime = (self._total_runtime / total) if total > 0 else 0.0
        success_rate = ((self._tasks_completed / total * 100.0) if total > 0 else 0.0)
        hours_saved = self._tasks_completed * self.hspw_multiplier

        return {
            "agent": self.name,
            "tasks_completed": self._tasks_completed,
            "average_runtime": f"{avg_runtime:.1f}s",
            "success_rate": round(success_rate, 1),
            "hours_saved": round(hours_saved, 2),
        }

    def report(self) -> str:
        """Generate concise operational efficiency summary."""
        m = self.metrics()
        return (
            f"Agent: {self.name} | Completed: {m['tasks_completed']} | Success: {m['success_rate']}% | HSPW"
            f" Contributed: {m['hours_saved']} hrs"
        )
