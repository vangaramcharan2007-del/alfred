"""Evaluation Drift Detector & Quality Trend Analyzer for Phase 102.7."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from jarvisx.evaluation.models import ResponseEvaluation
from jarvisx.evaluation.storage.feedback_memory import FeedbackMemory


class DriftSeverity(str, Enum):
    STABLE = "STABLE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class DriftReport:
    """Diagnostic report detecting long-term degradation in retrieval and grounding quality."""
    is_drift_detected: bool
    severity: DriftSeverity
    baseline_grounding: float
    current_grounding: float
    grounding_drop_pct: float
    baseline_correction_rate: float
    current_correction_rate: float
    correction_increase_pct: float
    total_evaluations_analyzed: int
    degraded_sources: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


class EvaluationDriftDetector:
    """Analyzes historical evaluation windows to detect quality degradation and trigger self-improvement."""

    def __init__(self, memory: FeedbackMemory):
        self.memory = memory

    def analyze_drift(self, window_size: int = 20, min_evals: int = 10) -> DriftReport:
        """Compare older baseline evaluations against recent window to detect drift."""
        all_evals = self.memory.list_recent_evaluations(limit=100)
        source_utilities = self.memory.get_all_source_utilities()

        if len(all_evals) < min_evals:
            return DriftReport(
                is_drift_detected=False,
                severity=DriftSeverity.STABLE,
                baseline_grounding=1.0,
                current_grounding=1.0,
                grounding_drop_pct=0.0,
                baseline_correction_rate=0.0,
                current_correction_rate=0.0,
                correction_increase_pct=0.0,
                total_evaluations_analyzed=len(all_evals),
                diagnostics=["Insufficient evaluation history for drift analysis."],
                recommended_actions=["Continue recording task evaluations."],
            )

        # Split into recent window vs baseline (older history)
        recent_window = all_evals[:min(window_size, len(all_evals) // 2 or len(all_evals))]
        baseline_window = all_evals[len(recent_window):] or recent_window

        # Grounding metrics
        recent_grounding = sum(e.grounding_score for e in recent_window) / len(recent_window)
        baseline_grounding = sum(e.grounding_score for e in baseline_window) / len(baseline_window)
        grounding_drop = max(0.0, baseline_grounding - recent_grounding)
        grounding_drop_pct = (grounding_drop / max(0.01, baseline_grounding)) * 100

        # Correction rate metrics
        recent_corrections = sum(1 for e in recent_window if e.is_user_accepted is False)
        recent_corr_rate = recent_corrections / len(recent_window)

        baseline_corrections = sum(1 for e in baseline_window if e.is_user_accepted is False)
        baseline_corr_rate = baseline_corrections / len(baseline_window)
        corr_increase = max(0.0, recent_corr_rate - baseline_corr_rate)
        corr_increase_pct = corr_increase * 100

        # Detect degraded sources (utility < 0.60 and corrected >= 2)
        degraded = [
            {
                "source_file": s.source_file,
                "utility_score": round(s.utility_score, 2),
                "times_corrected": s.times_corrected,
            }
            for s in source_utilities
            if s.utility_score < 0.65 and s.times_corrected >= 2
        ]

        # Determine severity and diagnostics
        diagnostics = []
        recommendations = []
        is_drift = False

        if grounding_drop_pct >= 25.0 or corr_increase_pct >= 30.0:
            severity = DriftSeverity.CRITICAL
            is_drift = True
            diagnostics.append(f"CRITICAL DRIFT: Grounding dropped by {round(grounding_drop_pct, 1)}% or correction rate spiked by {round(corr_increase_pct, 1)}%.")
            recommendations.append("Trigger Phase 97 Self-Improvement: Rebuild vector index embeddings and retire outdated notes.")
        elif grounding_drop_pct >= 12.0 or corr_increase_pct >= 15.0 or len(degraded) > 0:
            severity = DriftSeverity.WARNING
            is_drift = True
            diagnostics.append(f"WARNING: Moderate quality degradation detected (Grounding drop: {round(grounding_drop_pct, 1)}%, Correction rise: {round(corr_increase_pct, 1)}%).")
            recommendations.append("Inspect degraded vault notes and verify semantic index coverage.")
        else:
            severity = DriftSeverity.STABLE
            diagnostics.append("System quality metrics are stable and well-grounded.")
            recommendations.append("No corrective action required.")

        if degraded:
            diagnostics.append(f"Degraded sources detected: {[d['source_file'] for d in degraded]}")
            recommendations.append("Review or update the identified degraded knowledge notes in the Obsidian vault.")

        return DriftReport(
            is_drift_detected=is_drift,
            severity=severity,
            baseline_grounding=round(baseline_grounding, 4),
            current_grounding=round(recent_grounding, 4),
            grounding_drop_pct=round(grounding_drop_pct, 2),
            baseline_correction_rate=round(baseline_corr_rate, 4),
            current_correction_rate=round(recent_corr_rate, 4),
            correction_increase_pct=round(corr_increase_pct, 2),
            total_evaluations_analyzed=len(all_evals),
            degraded_sources=degraded,
            diagnostics=diagnostics,
            recommended_actions=recommendations,
        )
