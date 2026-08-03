from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from jarvisx.evolution.improvement_detector import ImprovementProposal

@dataclass
class SimulationResult:
    proposal_id: str
    expected_benefit_pct: float
    dependency_risk: str  # "LOW", "MEDIUM", "HIGH"
    safety_score: float
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "expected_benefit_pct": round(self.expected_benefit_pct, 1),
            "dependency_risk": self.dependency_risk,
            "safety_score": round(self.safety_score, 2),
            "recommendation": self.recommendation
        }

class EvolutionSimulator:
    def simulate_upgrade(self, proposal: ImprovementProposal) -> SimulationResult:
        prop_str = proposal.proposed_solution.lower()

        benefit = 20.0
        risk = "LOW"
        safety = 0.95

        if "security" in prop_str or "auth" in prop_str:
            benefit = 35.0
            risk = "MEDIUM"
            safety = 0.90
        elif "refactor" in prop_str or "rewrite" in prop_str:
            benefit = 15.0
            risk = "LOW"
            safety = 0.98

        rec = "PROCEED" if safety >= 0.80 else "APPROVAL_REQUIRED"

        return SimulationResult(
            proposal_id=proposal.proposal_id,
            expected_benefit_pct=benefit,
            dependency_risk=risk,
            safety_score=safety,
            recommendation=rec
        )
