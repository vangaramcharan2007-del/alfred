"""
Benchmark Reporter for formatting ALFRED AUTONOMY REPORT.
"""
from __future__ import annotations
from typing import List
from jarvisx.benchmark.runner import MissionExecutionResult
from jarvisx.benchmark.scoring import AutonomyScorer, AutonomyScoreResult


class BenchmarkReporter:
    @staticmethod
    def format_report(results: List[MissionExecutionResult], scores: AutonomyScoreResult) -> str:
        lines = []
        lines.append("\n" + "=" * 45)
        lines.append("        ALFRED BENCHMARK SUMMARY")
        lines.append("=" * 45)
        for r in results:
            status = "PASS" if r.success else "FAIL"
            lines.append(f"  [{status}] {r.mission_id}: {r.title} ({r.duration_sec:.2f}s)")
        lines.append("=" * 45 + "\n")

        lines.append("ALFRED AUTONOMY REPORT\n")
        lines.append(f"Planning: {int(scores.planning_score)}/100")
        lines.append(f"Execution: {int(scores.execution_score)}/100")
        lines.append(f"Recovery: {int(scores.recovery_score)}/100")
        lines.append(f"Memory: {int(scores.memory_score)}/100")
        lines.append(f"\nOverall Autonomy Score: {int(scores.overall_autonomy_score)}%\n")

        return "\n".join(lines)
