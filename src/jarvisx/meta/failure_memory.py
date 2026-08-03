from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class FailureRecord:
    task_description: str
    provider_id: str
    root_cause: str
    attempted_solution: str
    successful_fix: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_description": self.task_description,
            "provider_id": self.provider_id,
            "root_cause": self.root_cause,
            "attempted_solution": self.attempted_solution,
            "successful_fix": self.successful_fix,
            "timestamp": self.timestamp
        }

class FailureMemory:
    def __init__(self):
        self.failures: List[FailureRecord] = []

    def record_failure(
        self,
        task_description: str,
        provider_id: str,
        root_cause: str,
        attempted_solution: str,
        successful_fix: Optional[str] = None
    ) -> FailureRecord:
        rec = FailureRecord(
            task_description=task_description,
            provider_id=provider_id,
            root_cause=root_cause,
            attempted_solution=attempted_solution,
            successful_fix=successful_fix
        )
        self.failures.append(rec)
        return rec

    def find_similar_failures(self, keyword: str) -> List[FailureRecord]:
        kw = keyword.lower()
        return [f for f in self.failures if kw in f.task_description.lower() or kw in f.root_cause.lower()]
