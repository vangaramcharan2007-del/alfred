"""Evidence Trace Builder and Multi-Signal Claim Grounding Evaluator."""

from __future__ import annotations
import re
from typing import List, Set, Tuple
from jarvisx.evaluation.models import (
    ClaimEvidence,
    EvidenceSource,
    EvidenceSupportState,
    EvidenceTrace,
)
from jarvisx.knowledge.models import SearchResult


class EvidenceTracker:
    """Extracts claims from generated responses and validates their grounding against retrieved vault chunks."""

    STOPWORDS = {
        "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or",
        "is", "are", "was", "were", "be", "been", "does", "do", "how", "what",
        "why", "where", "which", "with", "this", "that", "it", "from", "by",
    }

    def build_trace(
        self,
        response_id: str,
        query: str,
        response_text: str,
        retrieved_chunks: List[SearchResult],
    ) -> EvidenceTrace:
        """Construct multi-signal evidence trace evaluating claim support states."""
        sentences = self._split_into_claims(response_text)
        if not sentences:
            sentences = [response_text.strip()] if response_text.strip() else ["No response generated."]

        claim_evaluations: List[ClaimEvidence] = []
        all_supporting_sources: List[EvidenceSource] = []
        seen_sources: Set[str] = set()

        supported_count = 0
        partially_count = 0
        unknown_count = 0
        unsupported_count = 0

        for sent in sentences:
            claim_state, confidence, sources = self._evaluate_claim_support(sent, retrieved_chunks)
            claim_evaluations.append(
                ClaimEvidence(
                    claim_text=sent,
                    support_state=claim_state,
                    confidence=confidence,
                    supporting_sources=sources,
                )
            )

            for s in sources:
                source_key = f"{s.source_file}:{s.section_heading}"
                if source_key not in seen_sources:
                    seen_sources.add(source_key)
                    all_supporting_sources.append(s)

            if claim_state == EvidenceSupportState.SUPPORTED:
                supported_count += 1
            elif claim_state == EvidenceSupportState.PARTIALLY_SUPPORTED:
                partially_count += 1
            elif claim_state == EvidenceSupportState.UNKNOWN_FROM_VAULT:
                unknown_count += 1
            else:
                unsupported_count += 1

        total_claims = len(sentences)
        # Grounding ratio: supported (1.0) + partially supported (0.5) / total
        grounding_ratio = (
            (supported_count * 1.0 + partially_count * 0.5) / max(1, total_claims)
        )

        return EvidenceTrace(
            response_id=response_id,
            query=query,
            claims=claim_evaluations,
            sources=all_supporting_sources,
            grounding_ratio=round(min(1.0, grounding_ratio), 4),
            supported_claims_count=supported_count,
            unknown_claims_count=unknown_count,
            unsupported_claims_count=unsupported_count,
        )

    def _split_into_claims(self, text: str) -> List[str]:
        """Split text into distinct claim sentences or list items."""
        # Split on newlines or sentence terminators
        raw_parts = re.split(r"(?<=[.!?])\s+|\n+|- |\* ", text)
        claims = []
        for p in raw_parts:
            cleaned = p.strip()
            # Ignore headers, markdown artifacts, or trivial snippets
            if cleaned and not cleaned.startswith("#") and len(cleaned) > 10:
                claims.append(cleaned)
        return claims

    def _evaluate_claim_support(
        self,
        claim: str,
        retrieved_chunks: List[SearchResult],
    ) -> Tuple[EvidenceSupportState, float, List[EvidenceSource]]:
        """Evaluate claim support state against retrieved chunks using multi-signal scoring."""
        if not retrieved_chunks:
            return EvidenceSupportState.UNKNOWN_FROM_VAULT, 0.0, []

        claim_norm = re.sub(r"[^\w\s]", " ", claim.lower().replace("-", " "))
        claim_tokens = {w for w in claim_norm.split() if w not in self.STOPWORDS and len(w) > 2}

        if not claim_tokens:
            return EvidenceSupportState.SUPPORTED, 1.0, []

        best_score = 0.0
        best_chunk: Optional[SearchResult] = None
        matched_sources: List[EvidenceSource] = []

        for chunk in retrieved_chunks:
            chunk_norm = re.sub(r"[^\w\s]", " ", chunk.content.lower().replace("-", " "))
            heading_norm = re.sub(r"[^\w\s]", " ", chunk.heading_path.lower().replace("-", " "))
            chunk_tokens = set(chunk_norm.split()) | set(heading_norm.split()) | {t.lower() for t in chunk.tags}

            # 1. Token overlap
            overlap = [w for w in claim_tokens if w in chunk_tokens or any(w in t or t in w for t in chunk_tokens if len(t) >= 4)]
            overlap_ratio = len(overlap) / max(1, len(claim_tokens))

            # 2. Substring or semantic similarity proxy
            score = (overlap_ratio * 0.7) + (min(1.0, chunk.score) * 0.3)

            if score > best_score:
                best_score = score
                best_chunk = chunk

            if overlap_ratio >= 0.4:
                matched_sources.append(
                    EvidenceSource(
                        source_file=chunk.source_file,
                        section_heading=chunk.heading_path,
                        confidence=round(score, 3),
                        chunk_id=chunk.chunk_id,
                        provenance_hash=chunk.provenance_hash,
                        matched_claim_snippet=claim[:100],
                    )
                )

        # Classify state
        if best_score >= 0.55:
            state = EvidenceSupportState.SUPPORTED
        elif best_score >= 0.30:
            state = EvidenceSupportState.PARTIALLY_SUPPORTED
        elif best_score >= 0.10:
            state = EvidenceSupportState.UNKNOWN_FROM_VAULT
        else:
            state = EvidenceSupportState.UNSUPPORTED

        return state, round(best_score, 3), matched_sources
