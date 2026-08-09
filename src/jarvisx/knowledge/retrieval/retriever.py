"""Hybrid Semantic & Knowledge Retriever with Security Scopes for Jarvis X."""

from __future__ import annotations
from typing import Dict, List, Optional
from jarvisx.knowledge.index.knowledge_index import KnowledgeMetadataIndex
from jarvisx.knowledge.index.vector_store import LocalVectorStore
from jarvisx.knowledge.models import (
    KnowledgeChunk,
    KnowledgeSensitivity,
    SearchResult,
    VaultCategory,
)
from jarvisx.knowledge.retrieval.ranking import HybridRanker


class KnowledgeRetriever:
    """Hybrid Retriever coordinating vector and metadata stores with role-based security filtering."""

    # Hierarchy of sensitivity access
    SENSITIVITY_HIERARCHY = {
        KnowledgeSensitivity.PUBLIC: 0,
        KnowledgeSensitivity.INTERNAL: 1,
        KnowledgeSensitivity.PRIVATE_NOTES: 2,
        KnowledgeSensitivity.SENSITIVE_MEMORY: 3,
    }

    def __init__(
        self,
        metadata_index: Optional[KnowledgeMetadataIndex] = None,
        vector_store: Optional[LocalVectorStore] = None,
        ranker: Optional[HybridRanker] = None,
    ):
        self.metadata_idx = metadata_index or KnowledgeMetadataIndex()
        self.vector_store = vector_store or LocalVectorStore()
        self.ranker = ranker or HybridRanker()

    def search(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[VaultCategory] = None,
        max_sensitivity: KnowledgeSensitivity = KnowledgeSensitivity.INTERNAL,
        actor_role: str = "AlfredMaster",
    ) -> List[SearchResult]:
        """Perform security-bounded hybrid search across the knowledge vault."""
        # 1. Retrieve all chunks from metadata index
        all_chunks = self.metadata_idx.list_all_chunks()
        if not all_chunks:
            return []

        # 2. Security & Category filtering
        max_level = self.SENSITIVITY_HIERARCHY.get(max_sensitivity, 1)
        # If actor is AlfredMaster or User, allow full access up to requested max_sensitivity
        if actor_role in ("AlfredMaster", "USER", "Alfred"):
            max_level = max(max_level, self.SENSITIVITY_HIERARCHY.get(max_sensitivity, 2))

        allowed_chunks: Dict[str, KnowledgeChunk] = {}
        for c in all_chunks:
            c_level = self.SENSITIVITY_HIERARCHY.get(c.sensitivity, 1)
            if c_level > max_level:
                continue
            if category_filter and c.category != category_filter:
                continue
            allowed_chunks[c.id] = c

        if not allowed_chunks:
            return []

        # 3. Dense vector search
        vector_matches = self.vector_store.search(query, top_k=top_k * 2)

        # 4. Filter vector matches to authorized chunks only
        filtered_vector_matches = [
            (cid, sim) for cid, sim in vector_matches if cid in allowed_chunks
        ]

        # 5. Hybrid ranking & fusion
        return self.ranker.rank_results(
            query=query,
            vector_matches=filtered_vector_matches,
            all_chunks_dict=allowed_chunks,
            top_k=top_k,
        )
