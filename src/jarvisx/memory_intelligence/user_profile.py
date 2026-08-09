"""User Profile Synthesizer for Phase 103 Memory Intelligence."""

from __future__ import annotations
from typing import List
from jarvisx.memory_intelligence.memory_store import MemoryStore
from jarvisx.memory_intelligence.models import MemoryType, UserProfile


class UserProfileSynthesizer:
    """Distills episodic, semantic, and procedural memories into an actionable cognitive persona."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def synthesize_profile(self) -> UserProfile:
        """Synthesize current user profile from active memories."""
        all_memories = self.store.list_memories(include_archived=False, limit=200)

        academic_track = "BTech CSE BDA"
        primary_goal = "Targeting 10 CGPA & Master DSA"
        learning_style = "Hands-on project implementation over pure theory"
        tech_prefs = ["Offline-first AI", "Python/Rust", "Obsidian Knowledge Vault"]
        recurring_habits: List[str] = []
        active_projects = ["Jarvis X Autonomous Personal OS"]
        strengths: List[str] = []
        weaknesses: List[str] = []

        for m in all_memories:
            content_lower = m.content.lower()

            if m.memory_type == MemoryType.SEMANTIC:
                if "btech" in content_lower or "cse" in content_lower or "bda" in content_lower:
                    academic_track = m.content
                elif "cgpa" in content_lower or "target" in content_lower or "goal" in content_lower:
                    primary_goal = m.content
                elif "prefer" in content_lower or "stack" in content_lower or "offline" in content_lower:
                    if m.content not in tech_prefs:
                        tech_prefs.append(m.content)

            elif m.memory_type == MemoryType.PROCEDURAL:
                if "learn" in content_lower or "study" in content_lower:
                    learning_style = m.content
                elif "habit" in content_lower or "routine" in content_lower or "daily" in content_lower:
                    recurring_habits.append(m.content)
                elif "struggle" in content_lower or "weak" in content_lower or "mistake" in content_lower:
                    weaknesses.append(m.content)

            elif m.memory_type == MemoryType.EPISODIC:
                if "completed" in content_lower or "passed" in content_lower or "mastered" in content_lower:
                    strengths.append(m.content)

        return UserProfile(
            name="User",
            academic_track=academic_track,
            primary_goal=primary_goal,
            preferred_learning_style=learning_style,
            technical_preferences=tech_prefs[:5],
            recurring_habits=recurring_habits[:5],
            active_projects=active_projects,
            known_strengths=strengths[:5],
            known_weaknesses=weaknesses[:5],
            total_memories_distilled=len(all_memories),
        )
