"""Operational Guardian Agent for Jarvis X.

Specialized background operational worker running periodic health checkups, git hygiene
inspections, and regression sweeps without disrupting executive workflow.
"""

from typing import Any, Dict, Optional
from jarvisx.agents.base import OperationalAgent
from jarvisx.automation.guardian import ProjectGuardian


class GuardianAgent(OperationalAgent):
    """Production background guardian monitoring builds, tests, and dependency hygiene."""

    __test__ = False

    def __init__(
        self,
        name: str = "guardian_agent",
        hspw_multiplier: float = 0.5,
        guardian: Optional[ProjectGuardian] = None,
    ):
        super().__init__(
            name=name,
            purpose="Continuous background monitoring of project builds, code health, git hygiene, and test regressions",
            capabilities=["build_monitoring", "regression_detection", "git_hygiene", "dependency_checking"],
            permissions=["read_filesystem", "git_status", "test_sandbox"],
            hspw_multiplier=hspw_multiplier,
        )
        self.guardian = guardian or ProjectGuardian()

    def _execute_task(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        action = (task.get("action") or task.get("parameters", {}).get("action", "sweep")).lower()
        target_dir = task.get("target_dir") or str(task.get("parameters", {}).get("target_dir", "."))
        self.guardian.target_dir = target_dir

        if action in ("sweep", "check", "monitor"):
            res = self.guardian.run_health_sweep()
            report = self.guardian.get_telemetry_report()
            return {
                "status": "completed",
                "action": "sweep",
                "overall_status": res["overall_status"],
                "alerts_count": len(res["alerts"]),
                "output": report["output"],
            }
        else:
            report = self.guardian.get_telemetry_report()
            return {
                "status": "completed",
                "action": "report",
                "overall_status": report["status"],
                "output": report["output"],
            }
