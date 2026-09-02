"""Data Models for Phase 97: Self Improvement Loop."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorClass(str, Enum):
    SYNTAX_ERROR = "SYNTAX_ERROR"
    TIMEOUT = "TIMEOUT"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    BAD_PLAN = "BAD_PLAN"
    BAD_DELEGATION = "BAD_DELEGATION"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"


class UpgradeStatus(str, Enum):
    PROPOSED = "PROPOSED"
    SANDBOX_TESTING = "SANDBOX_TESTING"
    VALIDATED = "VALIDATED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class PerformanceMetric:
    agent_name: str
    total_tasks: int
    successes: int
    failures: int
    success_rate: float
    avg_duration_sec: float
    confidence_score: float
    trend: str  # "UPWARD", "STABLE", "DEGRADING"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "total_tasks": self.total_tasks,
            "successes": self.successes,
            "failures": self.failures,
            "success_rate": round(self.success_rate, 3),
            "avg_duration_sec": round(self.avg_duration_sec, 3),
            "confidence_score": round(self.confidence_score, 2),
            "trend": self.trend,
        }


@dataclass
class FailureRootCause:
    failure_id: str
    error_class: ErrorClass
    failed_agent: str
    root_cause_category: str
    proposed_fix: str
    confidence: float
    recurrence_count: int
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "error_class": self.error_class.value,
            "failed_agent": self.failed_agent,
            "root_cause_category": self.root_cause_category,
            "proposed_fix": self.proposed_fix,
            "confidence": self.confidence,
            "recurrence_count": self.recurrence_count,
            "timestamp": self.timestamp,
        }


@dataclass
class SuccessPattern:
    pattern_id: str
    task_type: str
    strategy_template: List[str]
    success_rate: float
    sample_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "task_type": self.task_type,
            "strategy_template": self.strategy_template,
            "success_rate": round(self.success_rate, 2),
            "sample_count": self.sample_count,
        }


@dataclass
class UpgradeProposal:
    proposal_id: str
    target_component: str
    change_type: str  # PROMPT_TUNING, RETRY_POLICY, TIMEOUT_ADJUST, CAPABILITY_EXPANSION
    patch_diff: str
    validation_score: float
    status: UpgradeStatus
    rollback_plan: str
    created_at: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "target_component": self.target_component,
            "change_type": self.change_type,
            "patch_diff": self.patch_diff,
            "validation_score": self.validation_score,
            "status": self.status.value,
            "rollback_plan": self.rollback_plan,
            "created_at": self.created_at,
        }


@dataclass
class SandboxRun:
    run_id: str
    proposal_id: str
    tests_passed: int
    total_tests: int
    regression_detected: bool
    duration_sec: float
    status: str  # PASSED, REJECTED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "proposal_id": self.proposal_id,
            "tests_passed": self.tests_passed,
            "total_tests": self.total_tests,
            "regression_detected": self.regression_detected,
            "duration_sec": round(self.duration_sec, 3),
            "status": self.status,
        }
