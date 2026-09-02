"""Pre-generation Knowledge Retrieval Evaluator."""

from __future__ import annotations
from typing import List
from jarvisx.evaluation.models import RetrievalEvaluationResult
from jarvisx.knowledge.models import SearchResult


class RetrievalEvaluator:
    """Evaluates whether retrieved vault knowledge was relevant and sufficient for answering."""

    def evaluate_retrieval(
        self,
        query: str,
        retrieved_chunks: List[SearchResult],
    ) -> RetrievalEvaluationResult:
        """Evaluate retrieval relevance and confidence metrics."""
        if not retrieved_chunks:
            return RetrievalEvaluationResult(
                query=query,
                total_retrieved=0,
                top_score=0.0,
                mean_score=0.0,
                has_strong_grounding=False,
                retrieval_relevance_score=0.0,
                top_sources=[],
            )

        scores = [c.score for c in retrieved_chunks]
        top_score = max(scores)
        mean_score = sum(scores) / len(scores)

        # Strong grounding if top result has score >= 0.40 or tag/keyword match
        has_strong = top_score >= 0.40 or any("matched_keywords" in c.relevance_reason for c in retrieved_chunks[:2])

        # Relevance score combines top score and average depth
        relevance_score = (top_score * 0.7) + (mean_score * 0.3)

        top_sources = list(dict.fromkeys(c.source_file for c in retrieved_chunks[:3]))

        return RetrievalEvaluationResult(
            query=query,
            total_retrieved=len(retrieved_chunks),
            top_score=round(top_score, 4),
            mean_score=round(mean_score, 4),
            has_strong_grounding=has_strong,
            retrieval_relevance_score=round(min(1.0, relevance_score), 4),
            top_sources=top_sources,
        )
