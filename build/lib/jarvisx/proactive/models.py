"""Data Models for Phase 95: Proactive Intelligence Engine."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SignalType(str, Enum):
    ACADEMIC_RISK = "ACADEMIC_RISK"
    HABIT_DRIFT = "HABIT_DRIFT"
    GOAL_DEVIATION = "GOAL_DEVIATION"
    SCHEDULE_CONFLICT = "SCHEDULE_CONFLICT"


class InitiativeType(str, Enum):
    AUTO_DISPATCH = "AUTO_DISPATCH"       # High confidence (>0.80) -> dispatch mission
    SUGGEST_RECOVERY = "SUGGEST_RECOVERY" # Moderate confidence (0.50-0.79) -> briefing item
    ASK_CLARIFICATION = "ASK_CLARIFICATION" # Low confidence (<0.50) -> question


@dataclass
class RiskSignal:
    id: str
    type: SignalType
    source: str
    severity: float      # 0 - 100
    confidence: float    # 0.0 - 1.0
    reason: List[str]
    timestamp: float
    is_suppressed: bool = False  # e.g., if user marked vacation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "severity": self.severity,
            "confidence": self.confidence,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "is_suppressed": self.is_suppressed,
        }


@dataclass
class TrajectoryForecast:
    subject_or_goal: str
    current_mastery_pct: float
    current_weekly_hours: float
    days_to_target: int
    forecasted_score_pct: float
    required_hours_per_week: float
    cgpa_impact_delta: float
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject_or_goal": self.subject_or_goal,
            "current_mastery_pct": self.current_mastery_pct,
            "current_weekly_hours": self.current_weekly_hours,
            "days_to_target": self.days_to_target,
            "forecasted_score_pct": self.forecasted_score_pct,
            "required_hours_per_week": self.required_hours_per_week,
            "cgpa_impact_delta": self.cgpa_impact_delta,
            "explanation": self.explanation,
        }


@dataclass
class InitiativeDecision:
    id: str
    action_type: InitiativeType
    title: str
    target_subject: str
    mission_goal: str
    confidence: float
    reason: str
    dispatched: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_type": self.action_type.value,
            "title": self.title,
            "target_subject": self.target_subject,
            "mission_goal": self.mission_goal,
            "confidence": self.confidence,
            "reason": self.reason,
            "dispatched": self.dispatched,
        }
