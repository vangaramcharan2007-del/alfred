"""Master Memory Intelligence Engine Coordinator for Phase 103."""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional, Tuple

from jarvisx.memory_intelligence.context_builder import PersonalContextBuilder
from jarvisx.memory_intelligence.forgetting_engine import ForgettingEngine
from jarvisx.memory_intelligence.importance_ranker import MemoryImportanceRanker
from jarvisx.memory_intelligence.memory_extractor import MemoryExtractor
from jarvisx.memory_intelligence.memory_security import MemorySecurityGuard
from jarvisx.memory_intelligence.memory_store import MemoryStore
from jarvisx.memory_intelligence.models import (
    MemoryProvenance,
    MemoryRecord,
    MemorySensitivity,
    MemorySource,
    MemoryType,
    PersonalContextSummary,
    RelationType,
    UserProfile,
)
from jarvisx.memory_intelligence.relation_graph import MemoryRelationGraph
from jarvisx.memory_intelligence.user_profile import UserProfileSynthesizer


class MemoryIntelligenceEngine:
    """Master coordinator unifying extraction, importance scoring, relation graphs, decay models, and Alfred context."""

    def __init__(self, db_path: str = "var/db/memory_intelligence.db"):
        self.store = MemoryStore(db_path=db_path)
        self.security = MemorySecurityGuard()
        self.extractor = MemoryExtractor()
        self.ranker = MemoryImportanceRanker()
        self.graph = MemoryRelationGraph(self.store)
        self.forgetting = ForgettingEngine(self.store)
        self.profile_synthesizer = UserProfileSynthesizer(self.store)
        self.context_builder = PersonalContextBuilder(self.store)

    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SEMANTIC,
        sensitivity: MemorySensitivity = MemorySensitivity.PERSONAL,
        source_type: MemorySource = MemorySource.USER_EXPLICIT,
        evidence_text: str = "",
        source_ref: str = "",
        tags: Optional[List[str]] = None,
        actor_role: str = "AlfredMaster",
    ) -> Tuple[bool, Optional[MemoryRecord], Optional[str]]:
        """Explicitly store a memory with security validation and contradiction handling."""
        is_safe, reject_reason = MemorySecurityGuard.validate_memory_for_storage(content)
        if not is_safe:
            return False, None, reject_reason

        importance = self.ranker.compute_importance(
            content=content,
            memory_type=memory_type,
            source=source_type,
            user_explicit=(source_type == MemorySource.USER_EXPLICIT),
        )

        record = MemoryRecord(
            memory_type=memory_type,
            content=content,
            importance_score=importance,
            confidence=0.98 if source_type == MemorySource.USER_EXPLICIT else 0.90,
            sensitivity=sensitivity,
            provenance=MemoryProvenance(
                source_type=source_type,
                evidence_text=evidence_text or content,
                source_ref=source_ref,
                timestamp=time.time(),
            ),
            tags=tags or ["explicit"],
        )

        # 1. Save memory first to satisfy foreign key constraints
        self.store.save_memory(record)

        # 2. Contradiction Detection: resolve conflicts with older memories
        self.graph.detect_and_resolve_contradictions(record)

        return True, record, None

    def extract_and_store_from_conversation(
        self,
        text: str,
        source_ref: str = "",
    ) -> List[MemoryRecord]:
        """Automatically parse a conversation turn, extract non-trivial memories, and store them."""
        candidates = self.extractor.extract_candidates(
            text=text,
            source=MemorySource.CONVERSATION,
            source_ref=source_ref,
        )

        stored: List[MemoryRecord] = []
        for c in candidates:
            if c.should_store:
                success, record, _ = self.remember(
                    content=c.content,
                    memory_type=c.memory_type,
                    sensitivity=c.sensitivity,
                    source_type=c.source,
                    evidence_text=c.evidence,
                    source_ref=source_ref,
                    tags=c.tags,
                )
                if success and record:
                    stored.append(record)

        return stored

    def recall(
        self,
        query: str = "",
        memory_type: Optional[MemoryType] = None,
        actor_role: str = "AlfredMaster",
        limit: int = 20,
    ) -> List[MemoryRecord]:
        """Retrieve memories filtered by role access permissions."""
        all_memories = self.store.list_memories(memory_type=memory_type, include_archived=False, limit=limit * 2)
        accessible = [m for m in all_memories if MemorySecurityGuard.can_access_memory(m, actor_role=actor_role)]
        return accessible[:limit]

    def get_personal_context(
        self,
        query: str = "",
        actor_role: str = "AlfredMaster",
    ) -> PersonalContextSummary:
        """Compose personal context block for Alfred reasoning."""
        return self.context_builder.build_context(query=query, actor_role=actor_role)

    def get_user_profile(self) -> UserProfile:
        """Synthesize active user profile."""
        return self.profile_synthesizer.synthesize_profile()

    def audit_memory_health(self) -> Dict[str, Any]:
        """Perform system-wide memory health audit."""
        counts = self.store.count_memories()
        decay_candidates = self.forgetting.identify_decay_candidates()
        all_mem = self.store.list_memories(include_archived=True, limit=500)
        missing_provenance = sum(1 for m in all_mem if not m.provenance.source_type)

        return {
            "counts": counts,
            "decay_candidates_count": len(decay_candidates),
            "missing_provenance": missing_provenance,
        }
