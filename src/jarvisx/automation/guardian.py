"""Continuous Project Guardian & Background Telemetry for Jarvis X.

Performs periodic background diagnostic sweeps of git repositories, unit test health,
and workspace integrity to eliminate manual system checkups.
"""

from datetime import datetime
import os
from typing import Any, Dict, List, Optional

from jarvisx.automation.watchers import GitWatcher, PytestWatcher


class ProjectGuardian:
    """Autonomous background monitoring daemon tracking code hygiene and regression risks."""

    def __init__(self, target_dir: str = "."):
        self.target_dir = target_dir
        self.git_watcher = GitWatcher()
        self.test_watcher = PytestWatcher()
        self.last_sweep_timestamp: Optional[str] = None
        self.health_history: List[Dict[str, Any]] = []
        self._hours_saved: float = 0.0

    def run_health_sweep(self) -> Dict[str, Any]:
        """Execute a diagnostic checkup across git working state, unit tests, and build health."""
        git_res = self.git_watcher.check_git_status(cwd=self.target_dir)
        test_res = self.test_watcher.check_tests(cwd=self.target_dir)

        env_healthy = os.path.exists(os.path.join(self.target_dir, "pyproject.toml")) or os.path.exists(
            os.path.join(self.target_dir, "setup.py")
        )

        status = "HEALTHY"
        alerts: List[str] = []

        if git_res.get("status") == "DIRTY":
            count = git_res.get("uncommitted_count", 0)
            alerts.append(f"Git working tree dirty ({count} modified items uncommitted)")
        elif git_res.get("status") == "FAILED":
            status = "WARNING"
            alerts.append(f"Git check failed: {git_res.get('error')}")

        if test_res.get("status") in ("FAIL", "FAILED", "TIMEOUT"):
            status = "REGRESSION_DETECTED"
            alerts.append(f"Test regression detected: status={test_res.get('status')}")

        if not env_healthy and self.target_dir != ".":
            alerts.append("Missing project descriptor (pyproject.toml/setup.py)")

        sweep_result = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": status,
            "git": git_res,
            "tests": test_res,
            "env_healthy": env_healthy,
            "alerts": alerts,
        }
        self.last_sweep_timestamp = sweep_result["timestamp"]
        self.health_history.append(sweep_result)
        self._hours_saved += 0.4  # Eliminates ~25 minutes of manual testing and status checking
        return sweep_result

    def get_telemetry_report(self) -> Dict[str, Any]:
        """Synthesize executive background health telemetry for human supervisor review."""
        latest = self.health_history[-1] if self.health_history else self.run_health_sweep()
        status_icon = "✓" if latest["overall_status"] == "HEALTHY" else "⚠"

        report_lines = [
            "ALFRED PROJECT GUARDIAN TELEMETRY",
            f"Overall Status: {status_icon} {latest['overall_status']}",
            f"Last Diagnostic Sweep: {latest['timestamp']}",
            "",
            "Subsystem Status:",
            f"  • Git Working Tree: {latest['git'].get('status', 'UNKNOWN')} ({latest['git'].get('uncommitted_count', 0)} changes)",
            f"  • Test Suite Sandbox: {latest['tests'].get('status', 'UNKNOWN')}",
            f"  • Workspace Descriptor: {'VERIFIED' if latest['env_healthy'] else 'MISSING'}",
            "",
        ]

        if latest["alerts"]:
            report_lines.append("Actionable Alerts:")
            for alert in latest["alerts"]:
                report_lines.append(f"  [!] {alert}")
        else:
            report_lines.append("✓ Zero regressions or background conflicts detected.")

        return {
            "status": latest["overall_status"],
            "alerts_count": len(latest["alerts"]),
            "hours_saved": self._hours_saved,
            "output": "\n".join(report_lines),
        }
