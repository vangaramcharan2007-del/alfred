"""Initiative Engine (Autonomous Intervention Core) for Phase 95."""

from __future__ import annotations
import uuid
from typing import Dict, Any, List, Optional
from jarvisx.proactive.models import (
    InitiativeDecision,
    InitiativeType,
    RiskSignal,
    SignalType,
)
from jarvisx.proactive.proactive_memory import ProactiveMemory


class InitiativeEngine:
    """Evaluates declarative rules against RiskSignals and enforces confidence boundaries."""

    def __init__(self, memory: Optional[ProactiveMemory] = None):
        self.memory = memory or ProactiveMemory()

    def evaluate_signals_and_decide(self, signals: List[RiskSignal]) -> List[InitiativeDecision]:
        """Convert detected RiskSignals into calibrated proactive initiatives."""
        decisions: List[InitiativeDecision] = []

        for sig in signals:
            if sig.is_suppressed:
                continue

            decision_id = f"init_{str(uuid.uuid4())[:8]}"

            # Rule 1: High Confidence Academic Risk -> Autonomous Mission Dispatch
            if sig.type == SignalType.ACADEMIC_RISK and sig.confidence >= 0.80:
                d = InitiativeDecision(
                    id=decision_id,
                    action_type=InitiativeType.AUTO_DISPATCH,
                    title=f"Autonomous Revision: {sig.source}",
                    target_subject=sig.source,
                    mission_goal=f"Prepare crash revision notes and practice quiz for {sig.source}",
                    confidence=sig.confidence,
                    reason=f"High-confidence academic risk ({int(sig.confidence*100)}%): " + "; ".join(sig.reason),
                    dispatched=False,
                )
                self.memory.save_initiative(d)
                decisions.append(d)

            # Rule 2: Moderate Confidence Academic or Habit Risk -> Suggestion in Briefing
            elif sig.confidence >= 0.50:
                d = InitiativeDecision(
                    id=decision_id,
                    action_type=InitiativeType.SUGGEST_RECOVERY,
                    title=f"Study Recovery: {sig.source}",
                    target_subject=sig.source,
                    mission_goal=f"Suggested study block for {sig.source}",
                    confidence=sig.confidence,
                    reason=f"Moderate-confidence suggestion: " + "; ".join(sig.reason),
                    dispatched=False,
                )
                self.memory.save_initiative(d)
                decisions.append(d)

            # Rule 3: Low Confidence -> Ask Clarification
            else:
                d = InitiativeDecision(
                    id=decision_id,
                    action_type=InitiativeType.ASK_CLARIFICATION,
                    title=f"Check Context: {sig.source}",
                    target_subject=sig.source,
                    mission_goal="",
                    confidence=sig.confidence,
                    reason="Low signal confidence; requesting clarification.",
                    dispatched=False,
                )
                self.memory.save_initiative(d)
                decisions.append(d)

        return decisions
