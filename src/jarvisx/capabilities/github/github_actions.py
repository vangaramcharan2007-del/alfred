from __future__ import annotations
import time
from typing import Dict, Any, List, Optional

class GitHubActionsManager:
    def __init__(self):
        self._workflow_runs: Dict[str, Dict[str, Any]] = {
            "run_101": {
                "id": "run_101",
                "name": "CI Build & Test",
                "status": "completed",
                "conclusion": "success",
                "branch": "main",
                "timestamp": time.time() - 3600
            },
            "run_102": {
                "id": "run_102",
                "name": "Integration Test Suite",
                "status": "completed",
                "conclusion": "failure",
                "branch": "feature/ai-agent",
                "timestamp": time.time() - 1800
            }
        }

    def read_workflow_runs(self, repo_path: str) -> List[Dict[str, Any]]:
        return list(self._workflow_runs.values())

    def list_failed_workflows(self, repo_path: str) -> List[Dict[str, Any]]:
        return [r for r in self._workflow_runs.values() if r.get("conclusion") == "failure"]

    def retrieve_logs(self, run_id: str) -> str:
        run = self._workflow_runs.get(run_id)
        if not run:
            return f"No workflow run logs found for {run_id}."
        if run["conclusion"] == "failure":
            return f"=== Logs for {run_id} ({run['name']}) ===\n[ERROR] Test suite failure in tests/test_api.py line 42: ConnectionTimeout"
        return f"=== Logs for {run_id} ({run['name']}) ===\n[INFO] All 30 test cases passed cleanly."

    def trigger_workflow(self, workflow_id: str, ref: str = "main") -> Dict[str, Any]:
        run_id = f"run_{len(self._workflow_runs) + 101}"
        run_data = {
            "id": run_id,
            "name": workflow_id,
            "status": "in_progress",
            "conclusion": None,
            "branch": ref,
            "timestamp": time.time()
        }
        self._workflow_runs[run_id] = run_data
        return run_data

    def cancel_workflow(self, run_id: str) -> bool:
        if run_id in self._workflow_runs:
            self._workflow_runs[run_id]["status"] = "cancelled"
            self._workflow_runs[run_id]["conclusion"] = "cancelled"
            return True
        return False

    def summarize_failures(self, run_id: str) -> str:
        logs = self.retrieve_logs(run_id)
        if "ConnectionTimeout" in logs:
            return f"Workflow {run_id} failed due to ConnectionTimeout in tests/test_api.py."
        return f"Workflow {run_id} completed or has no detected critical failures."
