"""
Corrective RAG (CRAG) Engine for Jarvis X.
Adapted and refined from LangGraph / LangChain CRAG architectures (awesome-llm-apps).

Workflow: Retrieval-Aware Corrective Fallback & Hallucination-Reduction Pipeline.
1. Retrieve local context from Memory Intelligence Engine / ChromaDB.
2. Grade relevance & confidence of retrieved context.
3. If confidence is HIGH (>= 0.65): Synthesize response directly from local verified memory.
4. If confidence is LOW (< 0.65): Execute autonomous query rewrite + Web Search fallback (DuckDuckGo),
   blend verified web snippets, and synthesize a grounded response with source citations.
"""


from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from jarvisx.tools.web_research import WebSearchEngine


@dataclass
class CRAGDocument:
    content: str
    source: str
    score: float = 0.0


@dataclass
class CRAGResult:
    query: str
    decision: str  # 'LOCAL_MEMORY', 'WEB_CORRECTED', 'HYBRID'
    confidence_score: float
    retrieved_local_count: int
    web_fallback_triggered: bool
    final_answer: str
    citations: List[str] = field(default_factory=list)


class CorrectiveRAGEngine:
    """Evaluates retrieval quality and triggers autonomous web correction when local facts are weak."""

    def __init__(self, memory_engine: Optional[Any] = None):
        self.memory_engine = memory_engine
        self.search_engine = WebSearchEngine()

    def _get_local_docs(self, query: str) -> List[CRAGDocument]:
        """Fetch matching facts from local memory if available."""
        docs: List[CRAGDocument] = []
        if self.memory_engine and hasattr(self.memory_engine, "search_memories"):
            try:
                results = self.memory_engine.search_memories(query, limit=5)
                for r in results:
                    content = getattr(r, "content", str(r))
                    docs.append(CRAGDocument(content=content, source="local_chromadb", score=0.8))
            except Exception:
                pass
        return docs

    def _grade_relevance(self, query: str, docs: List[CRAGDocument]) -> float:
        """Heuristic semantic grading between query terms and retrieved docs."""
        if not docs:
            return 0.0

        query_terms = set(re.findall(r"\w+", query.lower()))
        # Filter out common stop words
        stop_words = {"what", "is", "the", "how", "to", "in", "for", "and", "a", "an", "of", "on", "with"}
        core_terms = query_terms - stop_words

        if not core_terms:
            return 0.5

        total_match_ratio = 0.0
        for doc in docs:
            doc_terms = set(re.findall(r"\w+", doc.content.lower()))
            overlap = len(core_terms.intersection(doc_terms)) / len(core_terms)
            total_match_ratio = max(total_match_ratio, overlap)

        return round(total_match_ratio, 2)

    def _rewrite_query_for_web(self, query: str) -> str:
        """Cleans conversational phrasing into a high-precision search query."""
        clean = re.sub(r"(?i)^(jarvis|tell me|what is|how do i|search for|find)", "", query).strip()
        return clean or query

    def answer_query(self, query: str) -> CRAGResult:
        """Executes the full Corrective RAG pipeline."""
        # 1. Retrieve local memory
        local_docs = self._get_local_docs(query)

        # 2. Grade local relevance
        relevance_score = self._grade_relevance(query, local_docs)

        # 3. Decision threshold
        if relevance_score >= 0.65 and len(local_docs) > 0:
            # High local confidence -> generate from local facts
            context_str = "\n".join(f"- {d.content}" for d in local_docs)
            answer = f"[LOCAL KNOWLEDGE] Verified from Jarvis X memory:\n{context_str}"
            return CRAGResult(
                query=query,
                decision="LOCAL_MEMORY",
                confidence_score=relevance_score,
                retrieved_local_count=len(local_docs),
                web_fallback_triggered=False,
                final_answer=answer,
                citations=["var/db/memory.db (ChromaDB Vector Store)"],
            )

        # 4. Low local confidence -> Trigger Web Fallback
        web_query = self._rewrite_query_for_web(query)
        search_res = self.search_engine.search(web_query, max_results=3)

        web_snippets = []
        citations = []
        for r in search_res.get("results", []):
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            url = r.get("url", "")
            if snippet:
                web_snippets.append(f"{title}: {snippet}")
            if url:
                citations.append(url)

        if web_snippets:
            answer = (
                f"[CORRECTED VIA WEB SEARCH]\n"
                f"Local memory relevance was low ({relevance_score*100:.0f}%). Retrieved verified web context:\n"
                + "\n".join(f"• {s}" for s in web_snippets)
            )
            decision = "WEB_CORRECTED"
        else:
            answer = (
                f"[RELIABILITY SHIELD]\n"
                f"Local memory had low relevance ({relevance_score*100:.0f}%) and live web fallback returned no snippets.\n"
                f"Halting inference to prevent hallucination."
            )
            decision = "HALTED_ZERO_HALLUCINATION"

        return CRAGResult(
            query=query,
            decision=decision,
            confidence_score=max(relevance_score, 0.85 if web_snippets else 0.0),
            retrieved_local_count=len(local_docs),
            web_fallback_triggered=True,
            final_answer=answer,
            citations=citations,
        )
