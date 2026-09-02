"""Hybrid Score Ranking & Fusion for Jarvis X Knowledge Subsystem."""

from __future__ import annotations
import re
from typing import Dict, List, Set, Tuple
from jarvisx.knowledge.models import KnowledgeChunk, SearchResult


class HybridRanker:
    """Combines dense semantic vector scores with keyword & tag matching using Reciprocal Rank Fusion."""

    STOPWORDS = {
        "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or",
        "is", "are", "was", "were", "be", "been", "does", "do", "how", "what",
        "why", "where", "which", "work", "works", "explain", "describe",
    }

    @staticmethod
    def _stem(word: str) -> str:
        w = word.lower()
        if w.endswith("ies") and len(w) > 4:
            return w[:-3] + "y"
        if w.endswith("es") and len(w) > 3:
            return w[:-2]
        if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
            return w[:-1]
        if w.endswith("ing") and len(w) > 4:
            return w[:-3]
        if w.endswith("ed") and len(w) > 3:
            return w[:-2]
        return w

    def rank_results(
        self,
        query: str,
        vector_matches: List[Tuple[str, float]],
        all_chunks_dict: Dict[str, KnowledgeChunk],
        top_k: int = 5,
    ) -> List[SearchResult]:
        """Fuse vector similarity scores and lexical keyword/tag overlap scores."""
        normalized_q = re.sub(r"[^\w\s]", " ", query.lower().replace("-", " "))
        all_q_words = set(normalized_q.split())
        # Significant query words with stopwords stripped
        content_words = {w for w in all_q_words if w not in self.STOPWORDS} or all_q_words
        content_stems = {self._stem(w) for w in content_words}
        scored_results: List[SearchResult] = []

        # Map vector similarity scores
        v_scores = {cid: score for cid, score in vector_matches}

        for cid, chunk in all_chunks_dict.items():
            norm_content = re.sub(r"[^\w\s]", " ", chunk.content.lower().replace("-", " "))
            norm_heading = re.sub(r"[^\w\s]", " ", chunk.heading_path.lower().replace("-", " "))
            tags_lower = {t.lower().replace("-", "") for t in chunk.tags}

            chunk_tokens = set(norm_content.split()) | set(norm_heading.split()) | tags_lower
            chunk_stems = {self._stem(t) for t in chunk_tokens}

            # 1. Lexical overlap score (on significant content words & stems)
            overlap_words = [
                w for w in content_words
                if w in chunk_tokens or self._stem(w) in chunk_stems or any(w in t or t in w for t in chunk_tokens if len(w) >= 4 and len(t) >= 4)
            ]
            lex_score = len(overlap_words) / max(1, len(content_words))

            # 2. Tag match boost
            tag_match = any(w in tags_lower or self._stem(w) in tags_lower for w in content_words)
            if tag_match:
                lex_score += 0.35

            # 3. Vector similarity score
            vec_score = v_scores.get(cid, 0.0)

            # 4. Combined weighted score (40% semantic vector + 60% content keyword/tag)
            final_score = (vec_score * 0.4) + (min(1.0, lex_score) * 0.6)

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
