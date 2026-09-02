"""Context Retriever for Jarvis X Memory Intelligence Layer (Layer 2 - Memory).

Retrieves relevant memories based on current task, conversation, objective, and deadlines.
"""

from typing import Any, Dict, List, Optional

from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider
from jarvisx.memory.intelligence.importance_engine import ImportanceEngine


class ContextRetriever:
    """Zero-fluff production context memory retriever."""

    def __init__(self, memory_provider: Optional[SQLiteMemoryProvider] = None):
        self.memory = memory_provider or SQLiteMemoryProvider(db_path="var/db/memory.db")
        self.importance_engine = ImportanceEngine()

    def retrieve_relevant_context(self, current_objective: str, category_filter: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memories matching objective and category with importance scoring."""
        if category_filter:
            raw_memories = self.memory.search_memory(category_filter, top_k=top_k * 2)
        else:
            raw_memories = self.memory.search_memory("voice_command", top_k=10) + self.memory.search_memory("goal", top_k=10)

        results = []
        for m in raw_memories:
            cat = m.get("category", "general")
            val = m.get("value", {})
            created_at = m.get("created_at", 0.0)

            score_info = self.importance_engine.compute_importance(
                frequency=val.get("frequency", 1),
                created_at=created_at,
                category=cat,
            )

            # Relevance match score
            match_score = 0.0
            obj_lower = current_objective.lower()
            text_corpus = str(val).lower() + " " + str(m.get("context", {})).lower()
            if obj_lower in text_corpus:
                match_score += 3.0

            total_rank = round(score_info["importance"] + match_score, 3)

            results.append({
                "memory_id": m.get("id"),
                "category": cat,
                "value": val,
                "importance": score_info["importance"],
                "rank_score": total_rank,
                "created_at": created_at,
            })

        results.sort(key=lambda x: x["rank_score"], reverse=True)
        return results[:top_k]
