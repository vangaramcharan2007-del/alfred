"""Memory Relation Graph & Contradiction Resolver for Phase 103."""

from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
from jarvisx.memory_intelligence.memory_store import MemoryStore
from jarvisx.memory_intelligence.models import MemoryRecord, MemoryRelation, RelationType


class MemoryRelationGraph:
    """Manages semantic and causal relationships between memories, detecting contradictions and resolving conflicts."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def link_memories(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        confidence: float = 1.0,
    ) -> MemoryRelation:
        """Create and store a directed relationship between two memories."""
        rel = MemoryRelation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            confidence=confidence,
        )
        self.store.add_relation(rel)
        return rel

    def get_related_memories(
        self,
        memory_id: str,
        relation_type: Optional[RelationType] = None,
    ) -> List[Tuple[MemoryRecord, RelationType]]:
        """Retrieve all memories connected to the given memory ID."""
        relations = self.store.get_relations_for_memory(memory_id)
        results: List[Tuple[MemoryRecord, RelationType]] = []

        for r in relations:
            if relation_type and r.relation_type != relation_type:
                continue
            other_id = r.target_id if r.source_id == memory_id else r.source_id
            other_mem = self.store.get_memory(other_id)
            if other_mem and not other_mem.is_archived:
                results.append((other_mem, r.relation_type))

        return results

    def detect_and_resolve_contradictions(
        self,
        new_memory: MemoryRecord,
    ) -> List[MemoryRecord]:
        """Detect existing memories that conflict with the new memory and archive or supersede them."""
        active_semantic = self.store.list_memories(memory_type=new_memory.memory_type, include_archived=False)
        conflicted: List[MemoryRecord] = []

        new_lower = new_memory.content.lower()

        # Simple semantic contradiction heuristics (e.g. OS switch, study change, preference shift)
        conflict_keywords = [
            ("windows", "linux"),
            ("mac", "linux"),
            ("prefer offline", "prefer cloud"),
            ("switched to", "previously used"),
            ("permanent switch", "using"),
        ]

        for old_mem in active_semantic:
            if old_mem.id == new_memory.id:
                continue

            old_lower = old_mem.content.lower()
            is_conflict = False

            for kw_a, kw_b in conflict_keywords:
                if (kw_a in new_lower and kw_b in old_lower) or (kw_b in new_lower and kw_a in old_lower):
                    is_conflict = True
                    break

            if is_conflict:
                # Link as CONFLICTS_WITH
                self.link_memories(
                    source_id=new_memory.id,
                    target_id=old_mem.id,
                    relation_type=RelationType.CONFLICTS_WITH,
                    confidence=0.95,
                )
                # Archive the older memory so it doesn't pollute current context
                self.store.archive_memory(old_mem.id)
                conflicted.append(old_mem)

        return conflicted
