from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class AttemptRecord:
    attempt_number: int
    changes_made: List[Dict[str, Any]] = field(default_factory=list)
    tests_executed: bool = False
    test_passed: bool = False
    failures: List[str] = field(default_factory=list)
    successful_fixes: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attempt_number": self.attempt_number,
            "changes_made": self.changes_made,
            "tests_executed": self.tests_executed,
            "test_passed": self.test_passed,
            "failures": self.failures,
            "successful_fixes": self.successful_fixes,
            "duration_seconds": round(self.duration_seconds, 3)
        }

class ExecutionHistory:
    def __init__(self, mission_id: Optional[str] = None):
        self.mission_id = mission_id or f"mission_{uuid.uuid4().hex[:8]}"
        self.attempts: List[AttemptRecord] = []

    def record_attempt(
        self,
        attempt_number: int,
        changes_made: List[Dict[str, Any]],
        tests_executed: bool = True,
        test_passed: bool = False,
        failures: Optional[List[str]] = None,
        successful_fixes: Optional[List[str]] = None,
        duration_seconds: float = 0.0
    ) -> AttemptRecord:
        record = AttemptRecord(
            attempt_number=attempt_number,
            changes_made=changes_made,
            tests_executed=tests_executed,
            test_passed=test_passed,
            failures=failures or [],
            successful_fixes=successful_fixes or [],
            duration_seconds=duration_seconds
        )
        self.attempts.append(record)
        return record

    def get_attempts(self) -> List[AttemptRecord]:
        return list(self.attempts)

    def get_successful_fixes(self) -> List[str]:
        fixes = []
        for a in self.attempts:
            fixes.extend(a.successful_fixes)
        return fixes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "total_attempts": len(self.attempts),
            "successful": any(a.test_passed for a in self.attempts),
            "attempts": [a.to_dict() for a in self.attempts]
        }
