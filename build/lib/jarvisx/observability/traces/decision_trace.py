from __future__ import annotations
from typing import Dict, Any, List, Optional

class DecisionTrace:
    """
    Records reasoning decisions, risk calculations, and confidence scores.
    """
    def __init__(self):
        self.decisions: List[Dict[str, Any]] = []

    def record_decision(self, intent: str, confidence: int, risk: str, rationale: str):
        self.decisions.append({
            "intent": intent,
            "confidence": confidence,
            "risk": risk,
            "rationale": rationale
        })

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_decisions": len(self.decisions),
            "decisions": self.decisions
        }
