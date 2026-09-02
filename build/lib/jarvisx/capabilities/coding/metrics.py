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
    registered_capabilities: int = 0
    provider_connections: int = 0
    mcp_connections: int = 0
    failed_connections: int = 0
    repositories_opened: int = 0
    issues_processed: int = 0
    prs_created: int = 0
    reviews_generated: int = 0
    workflow_runs: int = 0
    goose_sessions: int = 0
    goose_tasks: int = 0
    engineering_missions: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_task_duration: float = 0.0
    provider_selections: int = 0
    provider_failovers: int = 0
    provider_reroutes: int = 0
    selection_latency: float = 0.0
    provider_utilization: float = 0.0
    openhands_sessions: int = 0
    openhands_tasks: int = 0
    workspace_count: int = 0
    average_session_duration: float = 0.0
    provider_usage: int = 0
    llm_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    model_usage: int = 0
    fallback_count: int = 0
    hardware_usage: float = 0.0
    estimated_cost: float = 0.0
    capability_count: int = 0
    knowledge_gaps: int = 0
    improvement_plans: int = 0
    self_analysis_runs: int = 0
    failure_patterns: int = 0
    system_confidence: float = 0.95
    evolution_cycles: int = 0
    successful_upgrades: int = 0
    failed_upgrades: int = 0
    improvement_score: float = 0.90
    system_growth_rate: float = 0.15
    automation_level: float = 0.95
    capability_load_time: float = 0.0

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

    def record_capability_metrics(self, load_time: float = 0.0) -> None:
        self.registered_capabilities += 1
        self.capability_load_time += load_time

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
            "registered_capabilities": self.registered_capabilities,
            "provider_connections": self.provider_connections,
            "mcp_connections": self.mcp_connections,
            "failed_connections": self.failed_connections,
            "repositories_opened": self.repositories_opened,
            "issues_processed": self.issues_processed,
            "prs_created": self.prs_created,
            "reviews_generated": self.reviews_generated,
            "workflow_runs": self.workflow_runs,
            "goose_sessions": self.goose_sessions,
            "goose_tasks": self.goose_tasks,
            "engineering_missions": self.engineering_missions,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "average_task_duration": round(self.average_task_duration, 3),
            "provider_selections": self.provider_selections,
            "provider_failovers": self.provider_failovers,
            "provider_reroutes": self.provider_reroutes,
            "selection_latency": round(self.selection_latency, 4),
            "provider_utilization": round(self.provider_utilization, 3),
            "openhands_sessions": self.openhands_sessions,
            "openhands_tasks": self.openhands_tasks,
            "workspace_count": self.workspace_count,
            "average_session_duration": round(self.average_session_duration, 3),
            "provider_usage": self.provider_usage,
            "llm_requests": self.llm_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "model_usage": self.model_usage,
            "fallback_count": self.fallback_count,
            "hardware_usage": round(self.hardware_usage, 2),
            "estimated_cost": round(self.estimated_cost, 4),
            "capability_count": self.capability_count,
            "knowledge_gaps": self.knowledge_gaps,
            "improvement_plans": self.improvement_plans,
            "self_analysis_runs": self.self_analysis_runs,
            "failure_patterns": self.failure_patterns,
            "system_confidence": round(self.system_confidence, 3),
            "evolution_cycles": self.evolution_cycles,
            "successful_upgrades": self.successful_upgrades,
            "failed_upgrades": self.failed_upgrades,
            "improvement_score": round(self.improvement_score, 2),
            "system_growth_rate": round(self.system_growth_rate, 2),
            "automation_level": round(self.automation_level, 2),
            "capability_load_time": round(self.capability_load_time, 3),




            "total_execution_time_seconds": round(self.total_execution_time_seconds, 3),
            "average_execution_time": round(self.average_execution_time, 3),
        }







