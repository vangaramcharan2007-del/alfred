"""Deterministic Memory Importance Ranker for Phase 103."""

from __future__ import annotations
import re
from typing import Dict, List, Optional
from jarvisx.memory_intelligence.models import MemorySensitivity, MemorySource, MemoryType


class MemoryImportanceRanker:
    """Computes deterministic importance scores for memory retention.
    
    Formula:
    Importance = (Goal Relevance * 0.35) + (Repetition * 0.25) + (User Explicitness * 0.20) + (Future Usefulness * 0.20)
    """

    GOAL_KEYWORDS = {
        "cgpa", "exam", "syllabus", "midterm", "final", "btech", "cse", "dsa",
        "leetcode", "project", "jarvis", "release", "milestone", "career", "grade",
        "ai", "offline", "system", "os", "linux", "windows", "security", "vault", "model",
    }

    FUTURE_UTILITY_KEYWORDS = {
        "prefer", "always", "never", "routine", "schedule", "standard", "stack",
        "architecture", "workflow", "study", "habit", "switch", "rule", "learn", "build",
    }

    def compute_importance(
        self,
        content: str,
        memory_type: MemoryType,
        source: MemorySource,
        repetition_count: int = 1,
        user_explicit: bool = False,
    ) -> float:
        """Calculate normalized importance score between 0.0 and 1.0."""
        text_lower = content.lower()
        tokens = set(re.findall(r"\b\w+\b", text_lower))

        is_explicit = (
            source == MemorySource.USER_EXPLICIT
            or user_explicit
            or any(p in text_lower for p in ("remember that", "my preference is", "i always", "i never", "important:"))
        )

        # 1. Goal Relevance (0.0 to 1.0)
        goal_matches = len(tokens.intersection(self.GOAL_KEYWORDS))
        goal_rel = min(1.0, goal_matches * 0.35 + (0.50 if is_explicit else 0.0))
        if memory_type == MemoryType.EPISODIC and any(w in text_lower for w in ("completed", "released", "failed", "solved")):
            goal_rel = max(goal_rel, 0.85)

        # 2. Repetition (0.0 to 1.0)
        repetition = min(1.0, (repetition_count - 1) * 0.25 + (0.6 if is_explicit else 0.2))

        # 3. User Explicitness (0.0 to 1.0)
        if is_explicit:
            explicitness = 1.0
        elif source == MemorySource.CONVERSATION:
            explicitness = 0.5
        else:
            explicitness = 0.3

        # 4. Future Usefulness (0.0 to 1.0)
        util_matches = len(tokens.intersection(self.FUTURE_UTILITY_KEYWORDS))
        future_use = min(1.0, util_matches * 0.35 + (0.50 if is_explicit else 0.2))
        if memory_type in (MemoryType.PROCEDURAL, MemoryType.SEMANTIC):
            future_use = max(future_use, 0.75 if is_explicit else 0.50)

        # Composite weighted score
        importance = (goal_rel * 0.35) + (repetition * 0.25) + (explicitness * 0.20) + (future_use * 0.20)
        return round(min(1.0, max(0.05, importance)), 4)
