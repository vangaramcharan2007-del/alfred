"""Data Models for Phase 94: Personal OS Layer (Long-Term Life & Goal Management)."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class GoalStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    AT_RISK = "AT_RISK"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


@dataclass
class Milestone:
    id: str
    title: str
    deadline: str
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "deadline": self.deadline,
            "completed": self.completed,
        }


@dataclass
class Goal:
    id: str
    title: str
    category: str  # academic, engineering, career, health
    target_date: str
    progress_pct: float = 0.0
    status: GoalStatus = GoalStatus.ACTIVE
    risk_reason: Optional[str] = None
    milestones: List[Milestone] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "target_date": self.target_date,
            "progress_pct": self.progress_pct,
            "status": self.status.value,
            "risk_reason": self.risk_reason,
            "milestones": [m.to_dict() for m in self.milestones],
        }


@dataclass
class Evidence:
    type: str  # failed_quiz, no_revision, user_confusion, exam_weight
    description: str
    weight: float  # 0.0 - 1.0
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "description": self.description,
            "weight": self.weight,
            "timestamp": self.timestamp,
        }


@dataclass
class TopicMastery:
    subject: str
    unit: str
    topic: str
    mastery_score: float  # 0.0 - 100.0
    last_revision_days_ago: int = 0
    confidence: float = 0.5
    evidence: List[Evidence] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "unit": self.unit,
            "topic": self.topic,
            "mastery_score": self.mastery_score,
            "last_revision_days_ago": self.last_revision_days_ago,
            "confidence": self.confidence,
            "evidence": [e.to_dict() for e in self.evidence],
        }


@dataclass
class Subject:
    name: str
    credits: int
    importance_weight: float  # 0.0 - 1.0
    units: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "credits": self.credits,
            "importance_weight": self.importance_weight,
            "units": self.units,
        }


@dataclass
class HabitLog:
    date: str
    habit: str  # deep_work, leetcode, revision, exercise
    duration_hours: float
    category: str = "study"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "habit": self.habit,
            "duration_hours": self.duration_hours,
            "category": self.category,
        }


@dataclass
class DailyPriority:
    task: str
    score: float  # 0 - 100
    breakdown: Dict[str, float]  # weakness, deadline, goal, habit components
    explanation: str
    generated_mission_goal: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "score": self.score,
            "breakdown": self.breakdown,
            "explanation": self.explanation,
            "generated_mission_goal": self.generated_mission_goal,
        }
