"""Memory Importance Engine for Jarvis X Memory Intelligence Layer (Layer 2 - Memory).

Scores memory importance based on:
importance = frequency + recency + future_usefulness
"""

import math
import time
from typing import Any, Dict


class ImportanceEngine:
    """Zero-fluff production memory importance scoring engine."""

    def __init__(self, half_life_seconds: float = 86400.0):
        self.half_life = half_life_seconds

    def compute_importance(
        self,
        frequency: int = 1,
        created_at: float = 0.0,
        category: str = "general",
        reference_count: int = 0,
        now: float = 0.0,
    ) -> Dict[str, float]:
        """Calculate importance score: importance = frequency + recency + future_usefulness."""
        current_time = now or time.time()
        age = max(0.0, current_time - created_at)

        # 1. Frequency Score (scaled logarithmically)
        freq_score = math.log1p(max(0, frequency + reference_count)) * 2.0

        # 2. Recency Score (decaying exponential over time)
        recency_score = math.exp(-age / self.half_life) * 5.0

        # 3. Future Usefulness Score (heuristic weight by category)
        usefulness_weights = {
            "goal": 5.0,
            "deadline": 4.5,
            "preference": 4.0,
            "habit": 3.5,
            "task": 3.0,
            "knowledge": 2.5,
            "temporary context": 1.0,
        }
        usefulness_score = usefulness_weights.get(category.lower(), 2.0)

        total_importance = round(freq_score + recency_score + usefulness_score, 3)

        return {
            "importance": total_importance,
            "frequency_score": round(freq_score, 3),
            "recency_score": round(recency_score, 3),
            "future_usefulness_score": round(usefulness_score, 3),
        }
