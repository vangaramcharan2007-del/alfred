from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class CodingMetrics:
    coding_tasks_completed: int = 0
    successful_fixes: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    reviews_completed: int = 0
    auto_repairs_attempted: int = 0
    auto_repairs_succeeded: int = 0
    files_analyzed: int = 0
    dependencies_detected: int = 0
    risk_assessments: int = 0
    architecture_queries: int = 0
    architectures_designed: int = 0
    adrs_recorded: int = 0
    diagrams_generated: int = 0
    total_execution_time_seconds: float = 0.0

    @property
    def average_execution_time(self) -> float:
        if self.coding_tasks_completed == 0:
            return 0.0
        return self.total_execution_time_seconds / self.coding_tasks_completed

    def record_task_completed(self, duration_seconds: float, success: bool = True) -> None:
        self.coding_tasks_completed += 1
        self.total_execution_time_seconds += duration_seconds
        if success:
            self.successful_fixes += 1

    def record_test_run(self, passed: bool) -> None:
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def record_review(self) -> None:
        self.reviews_completed += 1

    def record_auto_repair(self, success: bool = True) -> None:
        self.auto_repairs_attempted += 1
        if success:
            self.auto_repairs_succeeded += 1

    def record_codebase_intelligence(self, files: int = 0, deps: int = 0, risks: int = 0, arch_queries: int = 0) -> None:
        self.files_analyzed += files
        self.dependencies_detected += deps
        self.risk_assessments += risks
        self.architecture_queries += arch_queries

    def record_architecture_design(self, adrs: int = 0, diagrams: int = 0) -> None:
        self.architectures_designed += 1
        self.adrs_recorded += adrs
        self.diagrams_generated += diagrams

    def to_dict(self) -> Dict[str, Any]:
        return {
            "coding_tasks_completed": self.coding_tasks_completed,
            "successful_fixes": self.successful_fixes,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "reviews_completed": self.reviews_completed,
            "auto_repairs_attempted": self.auto_repairs_attempted,
            "auto_repairs_succeeded": self.auto_repairs_succeeded,
            "files_analyzed": self.files_analyzed,
            "dependencies_detected": self.dependencies_detected,
            "risk_assessments": self.risk_assessments,
            "architecture_queries": self.architecture_queries,
            "architectures_designed": self.architectures_designed,
            "adrs_recorded": self.adrs_recorded,
            "diagrams_generated": self.diagrams_generated,
            "total_execution_time_seconds": round(self.total_execution_time_seconds, 3),
            "average_execution_time": round(self.average_execution_time, 3),
        }



