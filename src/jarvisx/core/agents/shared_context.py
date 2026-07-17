"""Shared Context — a single shared memory layer accessible by all agents."""
import json
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

SHARED_CONTEXT_DIR = "var/shared_context"


class SharedContext:
    """Thread-safe shared memory layer for evidence, history, artifacts, and learned failures."""

    _instance: Optional["SharedContext"] = None

    def __init__(self):
        self.evidence_cache: Dict[str, Dict[str, Any]] = {}
        self.completed_objectives: List[Dict[str, Any]] = []
        self.execution_artifacts: Dict[str, Any] = {}
        self.learned_failures: List[Dict[str, Any]] = []
        os.makedirs(SHARED_CONTEXT_DIR, exist_ok=True)

    @classmethod
    def get_instance(cls) -> "SharedContext":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def store_evidence(self, task_id: str, evidence: Dict[str, Any]):
        self.evidence_cache[task_id] = evidence

    def get_evidence(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.evidence_cache.get(task_id)

    def record_completed_objective(self, objective_data: Dict[str, Any]):
        self.completed_objectives.append(objective_data)

    def record_artifact(self, key: str, artifact: Any):
        self.execution_artifacts[key] = artifact

    def record_failure(self, failure_data: Dict[str, Any]):
        self.learned_failures.append(failure_data)

    def get_context_summary(self) -> Dict[str, Any]:
        return {
            "evidence_count": len(self.evidence_cache),
            "completed_objectives": len(self.completed_objectives),
            "artifacts_count": len(self.execution_artifacts),
            "learned_failures": len(self.learned_failures),
        }

    def persist(self):
        state = {
            "evidence_cache": self.evidence_cache,
            "completed_objectives": self.completed_objectives,
            "execution_artifacts": {k: str(v) for k, v in self.execution_artifacts.items()},
            "learned_failures": self.learned_failures,
        }
        filepath = os.path.join(SHARED_CONTEXT_DIR, "shared_state.json")
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def load(self):
        filepath = os.path.join(SHARED_CONTEXT_DIR, "shared_state.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
            self.evidence_cache = data.get("evidence_cache", {})
            self.completed_objectives = data.get("completed_objectives", [])
            self.learned_failures = data.get("learned_failures", [])
