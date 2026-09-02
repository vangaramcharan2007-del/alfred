"""Response Quality and Grounding Scorer."""

from __future__ import annotations
import re
from typing import List, Optional
from jarvisx.evaluation.models import (
    EvidenceTrace,
    ResponseEvaluation,
    RetrievalEvaluationResult,
)


class ResponseScorer:
    """Calculates multi-factor deterministic response quality scores and applies correction penalties."""

    def score_response(
        self,
        response_id: str,
        query: str,
        response_text: str,
        retrieval_eval: RetrievalEvaluationResult,
        evidence_trace: EvidenceTrace,
        actor_role: str = "AlfredMaster",
        user_correction_penalty: float = 0.0,
    ) -> ResponseEvaluation:
        """Compute composite response quality score."""
        # 1. Grounding Score (from evidence trace)
        grounding_score = evidence_trace.grounding_ratio

        # 2. Completeness Score (heuristic based on query word coverage & answer depth)
        completeness_score = self._estimate_completeness(query, response_text)

        # 3. Clarity Score (based on structure, absence of rambling, formatting)
        clarity_score = self._estimate_clarity(response_text)

        # 4. Retrieval Confidence
        retrieval_confidence = retrieval_eval.retrieval_relevance_score

        # Composite Base Score:
        # Grounding (40%) + Completeness (30%) + Clarity (15%) + Retrieval Confidence (15%)
        base_score = (
            (grounding_score * 0.40)
            + (completeness_score * 0.30)
            + (clarity_score * 0.15)
            + (retrieval_confidence * 0.15)
        )

        # Penalties: Deduct user correction penalty if present
        final_quality = max(0.0, min(1.0, base_score - user_correction_penalty))

        return ResponseEvaluation(
            response_id=response_id,
            query=query,
            answer_snippet=response_text[:300],
            grounding_score=round(grounding_score, 4),
            completeness_score=round(completeness_score, 4),
            clarity_score=round(clarity_score, 4),
            retrieval_confidence=round(retrieval_confidence, 4),
            user_correction_penalty=round(user_correction_penalty, 4),
            final_quality_score=round(final_quality, 4),
            actor_role=actor_role,
            evidence_trace=evidence_trace,
        )

    def _estimate_completeness(self, query: str, answer: str) -> float:
        """Estimate whether the answer addresses the query terms thoroughly."""
        q_norm = re.sub(r"[^\w\s]", " ", query.lower())
        q_tokens = [w for w in q_norm.split() if len(w) > 3]
        if not q_tokens:
            return 0.85

        ans_norm = answer.lower()
        matched = sum(1 for w in q_tokens if w in ans_norm)
        term_ratio = matched / len(q_tokens)

        # Length factor: answers between 50 and 1500 chars are optimal
        ans_len = len(answer.strip())
        if ans_len < 20:
            length_factor = 0.3
        elif ans_len < 60:
            length_factor = 0.6
        else:
            length_factor = 1.0

        return min(1.0, (term_ratio * 0.6) + (length_factor * 0.4))

    def _estimate_clarity(self, answer: str) -> float:
        """Estimate clarity and structured formatting of answer."""
        text = answer.strip()
        if not text:
            return 0.0

        score = 0.70
        # Check for structured lists or headings
        if any(marker in text for marker in ["\n- ", "\n* ", "\n1. ", "\n## ", "```"]):
            score += 0.20
        # Penalize excessive repetition or giant unspaced blocks
        if len(text) > 3000 and "\n" not in text:
            score -= 0.30

        return max(0.2, min(1.0, score))
