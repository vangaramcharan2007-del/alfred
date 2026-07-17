"""Agent Metrics — per-agent performance tracking with persistence."""
import json
import os
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

METRICS_DIR = "var/agent_metrics"


class AgentMetrics:
    """Tracks per-agent performance: completions, failures, retries, timing, delegations."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.retries = 0
        self.total_execution_time = 0.0
        self.delegation_count = 0
        self._task_start_times: Dict[str, float] = {}

    def start_task(self, task_id: str):
        self._task_start_times[task_id] = time.time()

    def complete_task(self, task_id: str):
        self.tasks_completed += 1
        if task_id in self._task_start_times:
            self.total_execution_time += time.time() - self._task_start_times.pop(task_id)

    def fail_task(self, task_id: str):
        self.tasks_failed += 1
        self._task_start_times.pop(task_id, None)

    def record_retry(self):
        self.retries += 1

    def record_delegation(self):
        self.delegation_count += 1

    @property
    def avg_execution_time(self) -> float:
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 0.0
        return self.total_execution_time / total

    @property
    def success_rate(self) -> float:
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 0.0
        return self.tasks_completed / total

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "retries": self.retries,
            "avg_execution_time": round(self.avg_execution_time, 3),
            "delegation_count": self.delegation_count,
            "success_rate": round(self.success_rate, 3),
        }

    def persist(self):
        os.makedirs(METRICS_DIR, exist_ok=True)
        filepath = os.path.join(METRICS_DIR, f"{self.agent_id}.json")
        with open(filepath, "w") as f:
            json.dump(self.get_metrics(), f, indent=2)
