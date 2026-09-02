"""Forgetting Engine & Exponential Memory Decay Model for Phase 103."""

from __future__ import annotations
import time
from typing import List, Tuple
from jarvisx.memory_intelligence.memory_store import MemoryStore
from jarvisx.memory_intelligence.models import MemoryRecord


class ForgettingEngine:
    """Calculates exponential memory decay, identifies fading memories, and cleans stale records."""

    def __init__(self, store: MemoryStore, decay_half_life_days: float = 180.0, prune_threshold: float = 0.15):
        self.store = store
        self.half_life_days = decay_half_life_days
        self.prune_threshold = prune_threshold

    def evaluate_memory_strength(self, memory: MemoryRecord, now: float = 0.0) -> float:
        """Compute current retained strength of a memory."""
        return memory.compute_decayed_strength(now=now or time.time())

    def identify_decay_candidates(self, now: float = 0.0) -> List[Tuple[MemoryRecord, float]]:
        """List active memories that have decayed below the retention threshold."""
        current_time = now or time.time()
        active_memories = self.store.list_memories(include_archived=False, limit=500)
        candidates: List[Tuple[MemoryRecord, float]] = []

        for m in active_memories:
            strength = self.evaluate_memory_strength(m, now=current_time)
            if strength < self.prune_threshold:
                candidates.append((m, strength))

        return candidates

    def prune_decayed_memories(self, now: float = 0.0) -> int:
        """Archive all memories whose current strength is below retention threshold."""
        decayed = self.identify_decay_candidates(now=now)
        count = 0
        for m, _ in decayed:
            if self.store.archive_memory(m.id):
                count += 1
        return count
