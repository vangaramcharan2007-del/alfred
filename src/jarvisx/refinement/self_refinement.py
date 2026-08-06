"""Autonomous Self-Refinement Engine for Jarvis X (Layer 2 - Intelligence).

Analyzes historical execution monitor quality scores and feedback variances from SQLite memory
to automatically refine planning effort multipliers, priority weights, and mission templates.
"""

from typing import Any, Dict, List, Optional

from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider


class SelfRefinementEngine:
    """Zero-fluff production autonomous self-refinement engine."""

    def __init__(self, memory_provider: Optional[SQLiteMemoryProvider] = None):
        self.memory = memory_provider or SQLiteMemoryProvider(db_path="var/db/memory.db")
        self.global_estimation_multiplier: float = 1.0

    def compute_refinement_parameters(self) -> Dict[str, Any]:
        """Analyze past feedback records and adjust planning refinement multipliers."""
        feedback_records = self.memory.search_memory("feedback_learning", top_k=20)

        if not feedback_records:
            return {
                "status": "nominal",
                "estimation_multiplier": 1.0,
                "refinements_applied": 0,
                "strategy": "Standard baseline parameters active.",
            }

        multipliers = []
        for r in feedback_records:
            val = r.get("value", {})
            mult = val.get("adjustment_multiplier", 1.0)
            multipliers.append(mult)

        avg_mult = round(sum(multipliers) / len(multipliers), 2)
        self.global_estimation_multiplier = avg_mult

        strategy = f"Self-refined planning multiplier set to {avg_mult}x based on {len(feedback_records)} historical execution feedback cycles."

        return {
            "status": "REFINED",
            "estimation_multiplier": avg_mult,
            "refinements_applied": len(feedback_records),
            "strategy": strategy,
        }
