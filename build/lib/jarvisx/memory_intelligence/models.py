"""Core Domain Models for Phase 103: Memory Intelligence Layer."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional
import uuid


class MemoryType(str, Enum):
    EPISODIC = "EPISODIC"       # What happened? Milestones, achievements, failures, sessions
    SEMANTIC = "SEMANTIC"       # What is true? Personal facts, preferences, constraints, background
    PROCEDURAL = "PROCEDURAL"   # How user works & learns? Habits, learning styles, heuristics


class MemorySource(str, Enum):
    USER_EXPLICIT = "USER_EXPLICIT"       # "Remember that I prefer offline AI"
    CONVERSATION = "CONVERSATION"         # Extracted from conversation turns
    KNOWLEDGE_LAYER = "KNOWLEDGE_LAYER"   # Linked from Obsidian vault
    SYSTEM_OBSERVED = "SYSTEM_OBSERVED"   # Inferred from mission completions / failures


class MemorySensitivity(str, Enum):
    PUBLIC = "PUBLIC"       # Safe for all agents & general context
    PERSONAL = "PERSONAL"   # Academic/work profile, goals, habits
    PRIVATE = "PRIVATE"     # Highly personal preferences, sensitive reflections
    SECRET = "SECRET"       # Passwords/tokens -> strictly rejected from memory store


class RelationType(str, Enum):
    SUPPORTS = "SUPPORTS"             # Memory A reinforces or supports Memory B
    CONFLICTS_WITH = "CONFLICTS_WITH" # Memory A contradicts Memory B (e.g. OS switch)
    CAUSED_BY = "CAUSED_BY"           # Memory A resulted from Memory B
    DERIVED_FROM = "DERIVED_FROM"     # Memory A is generalized from Memory B


@dataclass
class MemoryProvenance:
    """Cryptographic and contextual provenance trail for a memory."""
    source_type: MemorySource
    evidence_text: str = ""
    source_ref: str = ""        # Conversation ID, filename, or mission ID
    timestamp: float = field(default_factory=time.time)


@dataclass
class MemoryRecord:
    """A discrete unit of cognitive memory in Jarvis X."""
    id: str = field(default_factory=lambda: f"mem_{uuid.uuid4().hex[:10]}")
    memory_type: MemoryType = MemoryType.SEMANTIC
    content: str = ""
    importance_score: float = 0.5
    confidence: float = 0.9
    sensitivity: MemorySensitivity = MemorySensitivity.PERSONAL
    provenance: MemoryProvenance = field(default_factory=lambda: MemoryProvenance(source_type=MemorySource.CONVERSATION))
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    is_archived: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_decayed_strength(self, now: Optional[float] = None) -> float:
        """Compute current memory strength using exponential decay: S = I * e^(-days / 180)."""
        import math
        current_time = now if now is not None else time.time()
        age_days = max(0.0, (current_time - self.last_accessed_at) / 86400.0)
        decay = math.exp(-age_days / 180.0)
        reinforcement = 1.0 + (0.1 * min(5, self.access_count))
        return round(min(1.0, self.importance_score * decay * reinforcement), 4)


@dataclass
class MemoryRelation:
    """A directed semantic edge between two memories in the memory graph."""
    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float = 1.0
    created_at: float = field(default_factory=time.time)


@dataclass
class MemoryExtractionCandidate:
    """Candidate memory proposed by the MemoryExtractor."""
    content: str
    memory_type: MemoryType
    importance: float
    confidence: float
    sensitivity: MemorySensitivity
    source: MemorySource
    evidence: str
    tags: List[str] = field(default_factory=list)
    should_store: bool = True
    rejection_reason: Optional[str] = None


@dataclass
class UserProfile:
    """Consolidated cognitive model of user persona, goals, and working preferences."""
    name: str = "User"
    academic_track: str = "BTech CSE BDA"
    primary_goal: str = "Targeting 10 CGPA & Master DSA"
    preferred_learning_style: str = "Hands-on project implementation over pure theory"
    technical_preferences: List[str] = field(default_factory=lambda: ["Offline-first AI", "Python/Rust", "Obsidian Knowledge Vault"])
    recurring_habits: List[str] = field(default_factory=list)
    active_projects: List[str] = field(default_factory=lambda: ["Jarvis X Autonomous Personal OS"])
    known_strengths: List[str] = field(default_factory=list)
    known_weaknesses: List[str] = field(default_factory=list)
    total_memories_distilled: int = 0


@dataclass
class PersonalContextSummary:
    """Clean, token-capped context block prepared for injection into Alfred LLM prompts."""
    episodic_highlights: List[str] = field(default_factory=list)
    active_preferences: List[str] = field(default_factory=list)
    learning_style: str = ""
    goal_alignment: str = ""
    prompt_block: str = ""
