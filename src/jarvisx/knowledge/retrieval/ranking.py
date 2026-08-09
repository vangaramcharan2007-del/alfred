"""Hybrid Score Ranking & Fusion for Jarvis X Knowledge Subsystem."""

from __future__ import annotations
import re
from typing import Dict, List, Set, Tuple
from jarvisx.knowledge.models import KnowledgeChunk, SearchResult


class HybridRanker:
    """Combines dense semantic vector scores with keyword & tag matching using Reciprocal Rank Fusion."""

    def rank_results(
        self,
        query: str,
        vector_matches: List[Tuple[str, float]],
        all_chunks_dict: Dict[str, KnowledgeChunk],
        top_k: int = 5,
    ) -> List[SearchResult]:
        """Fuse vector similarity scores and lexical keyword/tag overlap scores."""
        q_words = set(re.sub(r"[^\w\s]", " ", query.lower()).split())
        scored_results: List[SearchResult] = []

        # Map vector similarity scores
        v_scores = {cid: score for cid, score in vector_matches}

        for cid, chunk in all_chunks_dict.items():
            content_lower = chunk.content.lower()
            heading_lower = chunk.heading_path.lower()
            tags_lower = {t.lower() for t in chunk.tags}

            # 1. Lexical overlap score
            overlap_words = [w for w in q_words if w in content_lower or w in heading_lower or w in tags_lower]
            lex_score = len(overlap_words) / max(1, len(q_words))

            # 2. Tag match boost
            tag_match = any(w in tags_lower for w in q_words)
            if tag_match:
                lex_score += 0.3

            # 3. Vector similarity score
            vec_score = v_scores.get(cid, 0.0)

            # 4. Combined weighted score (60% semantic vector + 40% lexical/tag)
            final_score = (vec_score * 0.6) + (min(1.0, lex_score) * 0.4)

            if final_score > 0.05 or overlap_words:
                reason_parts = []
                if vec_score > 0.3:
                    reason_parts.append(f"semantic_similarity ({round(vec_score, 2)})")
                if overlap_words:
                    reason_parts.append(f"matched_keywords [{', '.join(overlap_words[:3])}]")
                if tag_match:
                    reason_parts.append("tag_match")

                reason = " + ".join(reason_parts) if reason_parts else "general_relevance"

                scored_results.append(SearchResult(
                    chunk_id=chunk.id,
                    source_file=chunk.source_file,
                    content=chunk.content,
                    heading_path=chunk.heading_path,
                    score=final_score,
                    relevance_reason=reason,
                    sensitivity=chunk.sensitivity,
                    tags=chunk.tags,
                    provenance_hash=chunk.content_hash,
                ))

        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[:top_k]
