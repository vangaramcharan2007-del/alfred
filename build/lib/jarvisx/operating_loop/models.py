"""Data Models & Telemetry Schemas for the Phase 105 Autonomous Operating Loop."""

from __future__ import annotations
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class LoopStage(str, Enum):
    OBSERVE = "OBSERVE"
    UNDERSTAND = "UNDERSTAND"
    DECIDE = "DECIDE"
    PLAN = "PLAN"
    EXECUTE = "EXECUTE"
    EVALUATE = "EVALUATE"
    REMEMBER = "REMEMBER"
    IMPROVE = "IMPROVE"


@dataclass
class TopicMastery:
    topic_name: str
    domain: str  # e.g., "DSA", "Operating Systems", "DBMS", "Computer Networks", "ML"
    mastery_level: float = 0.50  # 0.0 to 1.0
    confidence: float = 0.80
    exam_proximity_days: Optional[int] = None
    past_failures_count: int = 0
    subtopics: List[str] = field(default_factory=list)
    last_practiced_at: float = field(default_factory=time.time)

    def calculate_priority_score(self) -> float:
        """Calculate dynamic study priority: Proximity * 0.40 + Weakness * 0.30 + Failures * 0.20 + Recency * 0.10."""
        # 1. Proximity factor (closer = higher score)
        if self.exam_proximity_days is not None:
            proximity_score = max(0.0, min(1.0, 1.0 - (self.exam_proximity_days / 30.0)))
        else:
            proximity_score = 0.3

        # 2. Weakness factor (lower mastery = higher priority)
        weakness_score = 1.0 - self.mastery_level

        # 3. Past failure factor
        failure_score = min(1.0, self.past_failures_count * 0.25)

        # 4. Recency factor (longer since practice = higher priority)
        days_since_practice = (time.time() - self.last_practiced_at) / 86400.0
        recency_score = min(1.0, days_since_practice / 7.0)

        return round(
            (proximity_score * 0.40)
            + (weakness_score * 0.30)
            + (failure_score * 0.20)
            + (recency_score * 0.10),
            3,
        )


@dataclass
class LearningProfile:
    degree: str = "BTech"
    domain: str = "Computer Science & Engineering (BDA)"
    primary_goal: str = "Targeting 10 CGPA & Master DSA"
    learning_style: str = "Hands-on project implementation over theory"
    topics: Dict[str, TopicMastery] = field(default_factory=dict)
    active_streak_days: int = 5
    last_streak_update: float = field(default_factory=time.time)


@dataclass
class StudyMission:
    mission_id: str = field(default_factory=lambda: f"mis_{uuid.uuid4().hex[:6]}")
    title: str = ""
    topic: str = ""
    estimated_minutes: int = 45
    reason: str = ""
    tasks: List[str] = field(default_factory=list)
    completed: bool = False
    created_at: float = field(default_factory=time.time)


@dataclass
class OperatingCycleResult:
    cycle_id: str = field(default_factory=lambda: f"cyc_{uuid.uuid4().hex[:8]}")
    timestamp: float = field(default_factory=time.time)
    observe: Dict[str, Any] = field(default_factory=dict)
    understand: Dict[str, Any] = field(default_factory=dict)
    decide: Dict[str, Any] = field(default_factory=dict)
    plan: Dict[str, Any] = field(default_factory=dict)
    execute: Dict[str, Any] = field(default_factory=dict)
    evaluate: Dict[str, Any] = field(default_factory=dict)
    remember: Dict[str, Any] = field(default_factory=dict)
    improve: Dict[str, Any] = field(default_factory=dict)
    total_latency_ms: float = 0.0
    status: str = "SUCCESS"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
