"""Initiative Arbiter for Phase 105: Autonomous Proaction vs User Interruption Guard."""

from __future__ import annotations
import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger("jarvisx.initiative_arbiter")


@dataclass
class InitiativeEvaluation:
    score: float
    decision: str  # "PROACT_NOTIFY", "SILENT_STORE", "DEFER"
    goal_impact: float
    urgency: float
    confidence: float
    user_availability: float
    explanation: str


class InitiativeArbiter:
    """Evaluates whether an ambient trigger warrants proactive intervention without spamming."""

    def __init__(self, confidence_threshold: float = 0.75, cooldown_seconds: float = 1800.0):
        self.confidence_threshold = confidence_threshold
        self.cooldown_seconds = cooldown_seconds
        self.last_proaction_time: float = 0.0

    def evaluate_initiative(
        self,
        goal_impact: float,
        urgency: float,
        confidence: float,
        user_availability: float = 0.80,
        override_cooldown: bool = False,
    ) -> InitiativeEvaluation:
        """Calculate Initiative Score = (Goal Impact * 0.35) + (Urgency * 0.25) + (Confidence * 0.20) + (Availability * 0.20)."""
        clamped_impact = max(0.0, min(1.0, goal_impact))
        clamped_urgency = max(0.0, min(1.0, urgency))
        clamped_confidence = max(0.0, min(1.0, confidence))
        clamped_avail = max(0.0, min(1.0, user_availability))

        score = round(
            (clamped_impact * 0.35)
            + (clamped_urgency * 0.25)
            + (clamped_confidence * 0.20)
            + (clamped_avail * 0.20),
            3,
        )

        now = time.time()
        time_since_last = now - self.last_proaction_time
        in_cooldown = (time_since_last < self.cooldown_seconds) and not override_cooldown

        if score >= self.confidence_threshold:
            if in_cooldown:
                decision = "SILENT_STORE"
                explanation = f"Score {score:.2f} >= {self.confidence_threshold:.2f}, but throttled by cooldown ({int(self.cooldown_seconds - time_since_last)}s remaining)."
            else:
                decision = "PROACT_NOTIFY"
                self.last_proaction_time = now
                explanation = f"High confidence proactive initiative ({score:.2f} >= {self.confidence_threshold:.2f})."
        else:
            decision = "SILENT_STORE"
            explanation = f"Low confidence initiative ({score:.2f} < {self.confidence_threshold:.2f}). Stored silently."

        return InitiativeEvaluation(
            score=score,
            decision=decision,
            goal_impact=clamped_impact,
            urgency=clamped_urgency,
            confidence=clamped_confidence,
            user_availability=clamped_avail,
            explanation=explanation,
        )
