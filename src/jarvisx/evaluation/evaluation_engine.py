"""Master EvaluationEngine Coordinator for Phase 102."""

from __future__ import annotations
import html
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import uuid

from jarvisx.evaluation.evidence.evidence_tracker import EvidenceTracker
from jarvisx.evaluation.models import (
    FailureCategory,
    FailureRecord,
    IntelligenceScorecard,
    ResponseEvaluation,
    RetrievalEvaluationResult,
)
from jarvisx.evaluation.scoring.quality_metrics import QualityMetricsAggregator
from jarvisx.evaluation.scoring.response_scorer import ResponseScorer
from jarvisx.evaluation.scoring.retrieval_evaluator import RetrievalEvaluator
from jarvisx.evaluation.storage.feedback_memory import FeedbackMemory
from jarvisx.knowledge.models import SearchResult


class EvaluationEngine:
    """Master coordinator for evidence-based response evaluation, feedback loops, and intelligence metrics."""

    def __init__(self, db_path: str = "var/db/evaluation.db"):
        self.memory = FeedbackMemory(db_path=db_path)
        self.evidence_tracker = EvidenceTracker()
        self.retrieval_evaluator = RetrievalEvaluator()
        self.response_scorer = ResponseScorer()
        self.metrics_aggregator = QualityMetricsAggregator(self.memory)

    def evaluate_response(
        self,
        query: str,
        answer: str,
        retrieved_chunks: List[SearchResult],
        actor_role: str = "AlfredMaster",
        response_id: Optional[str] = None,
    ) -> ResponseEvaluation:
        """Evaluate an agent response against retrieved evidence and persist score."""
        resp_id = response_id or f"resp_{uuid.uuid4().hex[:8]}"

        # 1. Evaluate pre-generation retrieval quality
        retrieval_eval = self.retrieval_evaluator.evaluate_retrieval(query, retrieved_chunks)

        # 2. Build multi-signal evidence trace
        evidence_trace = self.evidence_tracker.build_trace(
            response_id=resp_id,
            query=query,
            response_text=answer,
            retrieved_chunks=retrieved_chunks,
        )

        # 3. Compute composite response quality score
        eval_record = self.response_scorer.score_response(
            response_id=resp_id,
            query=query,
            response_text=answer,
            retrieval_eval=retrieval_eval,
            evidence_trace=evidence_trace,
            actor_role=actor_role,
        )

        # 4. Save to persistent SQLite storage
        self.memory.save_evaluation(eval_record)

        # 5. Track source utility metrics (initial retrieval)
        for src in evidence_trace.sources:
            self.memory.update_source_utility(
                source_file=src.source_file,
                retrieved=True,
                success=True if eval_record.grounding_score >= 0.5 else False,
                corrected=False,
            )

        return eval_record

    def record_user_correction(
        self,
        response_id: str,
        user_correction: str,
        category: FailureCategory = FailureCategory.FACTUAL_ERROR,
        cause: str = "User provided factual correction.",
        corrective_action: str = "Updated failure memory and penalized source utility.",
    ) -> Optional[ResponseEvaluation]:
        """Record user correction, penalize evaluation score, and log failure record for Phase 97 learning."""
        # Sanitize user input (prevent instruction injection)
        safe_correction = html.escape(user_correction.strip())

        failure_id = f"fail_{uuid.uuid4().hex[:8]}"
        failure = FailureRecord(
            failure_id=failure_id,
            response_id=response_id,
            category=category,
            cause=cause,
            user_correction=safe_correction,
            corrective_action=corrective_action,
        )
        self.memory.record_failure(failure)

        # Apply correction penalty (0.20 deduction)
        updated_eval = self.memory.record_feedback(
            response_id=response_id,
            is_accepted=False,
            user_feedback=safe_correction,
            correction_penalty=0.20,
        )

        # Update source utility records for affected sources
        if updated_eval and updated_eval.evidence_trace:
            for s in updated_eval.evidence_trace.sources:
                self.memory.update_source_utility(
                    source_file=s.source_file,
                    retrieved=False,
                    success=False,
                    corrected=True,
                )

        return updated_eval

    def record_user_acceptance(self, response_id: str, feedback: Optional[str] = None) -> Optional[ResponseEvaluation]:
        """Mark response as accepted by user with zero penalty."""
        return self.memory.record_feedback(
            response_id=response_id,
            is_accepted=True,
            user_feedback=feedback or "User accepted response without edits.",
            correction_penalty=0.0,
        )

    def get_last_evaluation(self) -> Optional[ResponseEvaluation]:
        """Retrieve most recent evaluation record."""
        return self.memory.get_last_evaluation()

    def get_evaluation(self, response_id: str) -> Optional[ResponseEvaluation]:
        """Retrieve specific evaluation record."""
        return self.memory.get_evaluation(response_id)

    def get_scorecard(self) -> IntelligenceScorecard:
        """Compute aggregated intelligence scorecard."""
        return self.metrics_aggregator.compute_scorecard()

    def list_history(self, limit: int = 20) -> List[ResponseEvaluation]:
        """List historical evaluations."""
        return self.memory.list_recent_evaluations(limit=limit)

    def get_source_utility_boost(self, source_file: str) -> float:
        """Get light, conservative utility multiplier (0.95 - 1.05) for knowledge ranking."""
        records = {r.source_file: r.utility_score for r in self.memory.get_all_source_utilities()}
        score = records.get(source_file, 1.0)
        # Conservative scaling: strictly clamped between 0.95 and 1.05
        raw_boost = 1.0 + ((score - 0.5) * 0.1)
        return max(0.95, min(1.05, round(raw_boost, 4)))
