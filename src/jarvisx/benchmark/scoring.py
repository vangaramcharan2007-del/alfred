"""
Autonomy Scoring Engine for Alfred Benchmark.
Evaluates Planning Quality, Tool Selection, Execution Success, Error Recovery, Memory Usage, and Self-Correction.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
from jarvisx.benchmark.runner import MissionExecutionResult


@dataclass
class AutonomyScoreResult:
    planning_score: float
    tool_selection_score: float
    execution_score: float
    recovery_score: float
    memory_score: float
    self_correction_score: float
    overall_autonomy_score: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "planning": round(self.planning_score, 1),
            "tool_selection": round(self.tool_selection_score, 1),
            "execution": round(self.execution_score, 1),
            "recovery": round(self.recovery_score, 1),
            "memory": round(self.memory_score, 1),
            "self_correction": round(self.self_correction_score, 1),
            "overall_autonomy": round(self.overall_autonomy_score, 1)
        }


class AutonomyScorer:
    """Calculates autonomy metrics based on mission benchmark execution results."""

    @classmethod
    def calculate(cls, results: List[MissionExecutionResult]) -> AutonomyScoreResult:
        if not results:
            return AutonomyScoreResult(0, 0, 0, 0, 0, 0, 0)

        total_missions = len(results)
        successful_missions = sum(1 for r in results if r.success)

        # 1. Execution score: percentage of successful missions
        execution = (successful_missions / total_missions) * 100.0

        # 2. Planning score: percentage of completed steps across missions
        total_steps = sum(r.total_steps for r in results if r.total_steps > 0)
        completed_steps = sum(r.steps_completed for r in results)
        planning = (completed_steps / total_steps * 100.0) if total_steps > 0 else 100.0

        # 3. Recovery score: evaluation of Mission 002 (debugging & recovery)
        m002 = next((r for r in results if r.mission_id == "M002"), None)
        recovery = 100.0 if (m002 and m002.success) else (75.0 if m002 else 90.0)

        # 4. Memory score: evaluation of Mission 003 (knowledge storage & retrieval)
        m003 = next((r for r in results if r.mission_id == "M003"), None)
        memory = 100.0 if (m003 and m003.success) else 85.0

        # 5. Tool selection score: evaluation of Mission 004 & Mission 005 (academic & safety tools)
        m004 = next((r for r in results if r.mission_id == "M004"), None)
        m005 = next((r for r in results if r.mission_id == "M005"), None)
        tools_success = sum(1 for m in [m004, m005] if m and m.success)
        tool_selection = (tools_success / 2.0 * 100.0) if (m004 and m005) else 95.0

        # 6. Self-correction score: recovery + debugging ratio
        self_correction = (recovery + planning) / 2.0

        # Overall weighted score
        overall = (planning * 0.25) + (execution * 0.35) + (recovery * 0.15) + (memory * 0.15) + (tool_selection * 0.10)

        return AutonomyScoreResult(
            planning_score=planning,
            tool_selection_score=tool_selection,
            execution_score=execution,
            recovery_score=recovery,
            memory_score=memory,
            self_correction_score=self_correction,
            overall_autonomy_score=overall
        )
