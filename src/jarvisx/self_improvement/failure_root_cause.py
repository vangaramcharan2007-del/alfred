"""Failure Root Cause Engine for Phase 97 Self Improvement Loop."""

from __future__ import annotations
import time
from typing import Dict, List, Optional
from jarvisx.self_improvement.models import ErrorClass, FailureRootCause
from jarvisx.self_improvement.self_improvement_memory import SelfImprovementMemory


class FailureRootCauseEngine:
    """Classifies multi-agent errors, tracks recurrence counts, and formulates deterministic recovery patches."""

    def __init__(self, memory: Optional[SelfImprovementMemory] = None):
        self.memory = memory or SelfImprovementMemory()

    def diagnose_failure(
        self,
        error_class: ErrorClass,
        failed_agent: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> FailureRootCause:
        """Analyze a runtime error and produce an explainable root cause report."""
        rec_count = 1
        existing = [f for f in self.memory.list_failures() if f.error_class == error_class and f.failed_agent == failed_agent]
        if existing:
            rec_count = existing[0].recurrence_count + 1

        if error_class == ErrorClass.BAD_DELEGATION:
            category = "Alfred delegated engineering task without complete OpenAPI specifications from Researcher"
            fix = "Enforce Researcher precondition schema before Coder dispatch"
            conf = 0.94
        elif error_class == ErrorClass.MISSING_DEPENDENCY:
            category = "Execution environment missing third-party python package"
            fix = "Friday auto-executes dependency sandbox installation"
            conf = 0.98
        elif error_class == ErrorClass.TIMEOUT:
            category = "Subtask exceeded 5.0s latency SLA threshold"
            fix = "Tune subtask timeout from 5.0s -> 10.0s with exponential backoff"
            conf = 0.91
        elif error_class == ErrorClass.SYNTAX_ERROR:
            category = "Generated python file contained unexpected syntax token"
            fix = "Run AST verification pass in Coder before file write"
            conf = 0.99
        else:
            category = f"Generic operational error in {failed_agent}: {error_message}"
            fix = "Add retry policy with exponential jitter"
            conf = 0.85

        report = FailureRootCause(
            failure_id=f"fail_{int(time.time()*1000)}",
            error_class=error_class,
            failed_agent=failed_agent,
            root_cause_category=category,
            proposed_fix=fix,
            confidence=conf,
            recurrence_count=rec_count,
            timestamp=time.time()
        )

        self.memory.record_failure(report)
        return report

    def list_diagnoses(self) -> List[FailureRootCause]:
        return self.memory.list_failures()
