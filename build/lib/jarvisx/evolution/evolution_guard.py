from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.evolution.improvement_detector import ImprovementProposal

class EvolutionGuard:
    def __init__(self, require_approval_for_high_risk: bool = True):
        self.require_approval = require_approval_for_high_risk

    def evaluate_safety(self, proposal: ImprovementProposal) -> Dict[str, Any]:
        sol_lower = proposal.proposed_solution.lower()

        # Violation checks
        if "delete capability" in sol_lower or "remove memory" in sol_lower:
            return {
                "safe": False,
                "approval_required": True,
                "reason": "Forbidden action: Modifying core memory or deleting capabilities is disallowed."
            }

        if any(w in sol_lower for w in ["security", "auth", "migration", "external"]):
            return {
                "safe": True,
                "approval_required": True,
                "reason": "High-risk change or external integration requires explicit approval."
            }

        return {
            "safe": True,
            "approval_required": False,
            "reason": "Low-risk upgrade passed safety guard policy."
        }
