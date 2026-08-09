"""System-wide Intelligence Quality Metrics Aggregator."""

from __future__ import annotations
from typing import Any, Dict, List
from jarvisx.evaluation.models import IntelligenceScorecard
from jarvisx.evaluation.storage.feedback_memory import FeedbackMemory


class QualityMetricsAggregator:
    """Aggregates historical evaluation records into high-level intelligence scorecards."""

    def __init__(self, memory: FeedbackMemory):
        self.memory = memory

    def compute_scorecard(self, limit: int = 50) -> IntelligenceScorecard:
        """Compute aggregate intelligence scorecard across recent evaluations."""
        recent_evals = self.memory.list_recent_evaluations(limit=limit)
        failures = self.memory.list_failures(limit=limit)
        source_utilities = self.memory.get_all_source_utilities()

        if not recent_evals:
            return IntelligenceScorecard(
                total_evaluations=0,
                average_grounding_score=1.0,
                average_quality_score=1.0,
                user_satisfaction_rate=1.0,
                total_failures_recorded=len(failures),
                top_utility_sources=[],
                recent_evaluations=[],
            )

        avg_grounding = sum(e.grounding_score for e in recent_evals) / len(recent_evals)
        avg_quality = sum(e.final_quality_score for e in recent_evals) / len(recent_evals)

        accepted_count = sum(1 for e in recent_evals if e.is_user_accepted is True)
        reviewed_count = sum(1 for e in recent_evals if e.is_user_accepted is not None)
        satisfaction_rate = (accepted_count / max(1, reviewed_count)) if reviewed_count > 0 else 1.0

        top_sources = [
            {
                "source_file": su.source_file,
                "times_retrieved": su.times_retrieved,
                "utility_score": round(su.utility_score, 3),
            }
            for su in source_utilities[:5]
        ]

        recent_summary = [
            {
                "response_id": e.response_id,
                "query": e.query,
                "grounding": round(e.grounding_score, 2),
                "quality": round(e.final_quality_score, 2),
                "accepted": e.is_user_accepted,
            }
            for e in recent_evals[:5]
        ]

        return IntelligenceScorecard(
            total_evaluations=len(recent_evals),
            average_grounding_score=round(avg_grounding, 4),
            average_quality_score=round(avg_quality, 4),
            user_satisfaction_rate=round(satisfaction_rate, 4),
            total_failures_recorded=len(failures),
            top_utility_sources=top_sources,
            recent_evaluations=recent_summary,
        )
