"""Alfred Personal Context Builder for Phase 103."""

from __future__ import annotations
import re
from typing import List, Optional, Set
from jarvisx.memory_intelligence.memory_security import MemorySecurityGuard
from jarvisx.memory_intelligence.memory_store import MemoryStore
from jarvisx.memory_intelligence.models import (
    MemoryRecord,
    MemoryType,
    PersonalContextSummary,
)


class PersonalContextBuilder:
    """Retrieves relevant personal, episodic, and procedural memories and composes a clean prompt block for Alfred."""

    STOP_WORDS: Set[str] = {
        "what", "is", "a", "an", "the", "in", "on", "at", "to", "for", "of", "and",
        "or", "it", "this", "that", "i", "my", "me", "you", "your", "do", "how",
        "why", "can", "should", "tell", "explain", "give", "please", "be", "have",
        "am", "about", "with", "by", "from"
    }

    def __init__(self, store: MemoryStore):
        self.store = store

    def build_context(
        self,
        query: str = "",
        actor_role: str = "AlfredMaster",
        max_items: int = 6,
    ) -> PersonalContextSummary:
        """Retrieve memories relevant to the query while filtering by role permissions."""
        all_memories = self.store.list_memories(include_archived=False, limit=50)

        # Filter by role security
        accessible = [m for m in all_memories if MemorySecurityGuard.can_access_memory(m, actor_role=actor_role)]

        query_tokens = set(re.findall(r"\b\w+\b", query.lower())) if query else set()
        meaningful_query_tokens = {t for t in query_tokens if t not in self.STOP_WORDS}

        # Check if query is asking for personal/planning/work context
        is_personal_query = not meaningful_query_tokens or any(
            w in meaningful_query_tokens for w in (
                "plan", "goal", "schedule", "work", "next", "jarvis", "project", "target",
                "preference", "prefer", "study", "learning", "semester", "cgpa", "exam", "focus"
            )
        )

        def score_mem(m: MemoryRecord) -> float:
            content_tokens = set(re.findall(r"\b\w+\b", m.content.lower()))
            meaningful_content = {t for t in content_tokens if t not in self.STOP_WORDS}
            overlap = len(meaningful_query_tokens.intersection(meaningful_content)) if meaningful_query_tokens else 1
            strength = m.compute_decayed_strength()

            if meaningful_query_tokens:
                if overlap == 0 and not is_personal_query:
                    return 0.0
                goal_boost = 3.0 if (is_personal_query and ("goal" in m.content.lower() or "cgpa" in m.content.lower() or m.memory_type == MemoryType.PROCEDURAL)) else 0.0
                return (overlap * 4.0) + (strength * 1.5) + goal_boost
            else:
                return strength * 1.5

        candidates = [m for m in accessible if score_mem(m) > 0.0] if (meaningful_query_tokens and not is_personal_query) else accessible
        ranked = sorted(candidates, key=score_mem, reverse=True)[:max_items]

        # If candidates are not relevant to non-personal query, return empty
        if meaningful_query_tokens and not is_personal_query and not any(score_mem(m) > 1.0 for m in ranked):
            return PersonalContextSummary(
                episodic_highlights=[],
                active_preferences=[],
                learning_style="",
                goal_alignment="",
                prompt_block="",
            )

        episodic: List[str] = []
        preferences: List[str] = []
        learning_style = ""
        goal_alignment = ""

        for m in ranked:
            if m.memory_type == MemoryType.EPISODIC:
                episodic.append(m.content)
            elif m.memory_type == MemoryType.SEMANTIC:
                preferences.append(m.content)
                if "cgpa" in m.content.lower() or "goal" in m.content.lower():
                    goal_alignment = m.content
            elif m.memory_type == MemoryType.PROCEDURAL:
                if not learning_style:
                    learning_style = m.content

        # Build prompt markdown block
        if not (goal_alignment or learning_style or preferences or episodic):
            return PersonalContextSummary(
                episodic_highlights=[],
                active_preferences=[],
                learning_style="",
                goal_alignment="",
                prompt_block="",
            )

        lines = [
            "### [PERSONAL MEMORY & USER CONTEXT]",
        ]
        if goal_alignment:
            lines.append(f"- **Primary Goal:** {goal_alignment}")
        if learning_style:
            lines.append(f"- **Learning/Work Style:** {learning_style}")
        if preferences:
            lines.append(f"- **User Preferences:** {'; '.join(preferences[:3])}")
        if episodic:
            lines.append(f"- **Recent Achievements/Context:** {'; '.join(episodic[:2])}")

        prompt_block = "\n".join(lines)

        return PersonalContextSummary(
            episodic_highlights=episodic,
            active_preferences=preferences,
            learning_style=learning_style,
            goal_alignment=goal_alignment,
            prompt_block=prompt_block,
        )

