"""Alfred Personal Context Builder for Phase 103."""

from __future__ import annotations
import re
from typing import List, Optional
from jarvisx.memory_intelligence.memory_security import MemorySecurityGuard
from jarvisx.memory_intelligence.memory_store import MemoryStore
from jarvisx.memory_intelligence.models import (
    MemoryRecord,
    MemoryType,
    PersonalContextSummary,
)


class PersonalContextBuilder:
    """Retrieves relevant personal, episodic, and procedural memories and composes a clean prompt block for Alfred."""

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

        # Score relevance to query tokens if query provided
        query_tokens = set(re.findall(r"\b\w+\b", query.lower())) if query else set()

        def score_mem(m: MemoryRecord) -> float:
            content_tokens = set(re.findall(r"\b\w+\b", m.content.lower()))
            overlap = len(query_tokens.intersection(content_tokens)) if query_tokens else 1
            strength = m.compute_decayed_strength()
            return (overlap * 2.0) + (strength * 1.5)

        ranked = sorted(accessible, key=score_mem, reverse=True)[:max_items]

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
