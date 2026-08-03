from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ImprovementProposal:
    proposal_id: str
    problem: str
    proposed_solution: str
    priority: str  # "HIGH", "MEDIUM", "LOW"
    risk_level: str = "LOW"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "problem": self.problem,
            "proposed_solution": self.proposed_solution,
            "priority": self.priority,
            "risk_level": self.risk_level
        }

class ImprovementDetector:
    def detect_proposals(self, meta_report: Dict[str, Any]) -> List[ImprovementProposal]:
        proposals: List[ImprovementProposal] = []

        # 1. Inspect missing capabilities or recommendations
        plans = meta_report.get("improvement_plans", [])
        for plan in plans:
            pid = f"prop_{uuid.uuid4().hex[:6]}"
            sol = "; ".join(plan.get("action_items", ["Integrate MCP tool"]))
            proposals.append(ImprovementProposal(
                proposal_id=pid,
                problem=plan.get("problem_statement", "System capability gap detected"),
                proposed_solution=f"{plan.get('title')}: {sol}",
                priority="HIGH" if plan.get("priority") == 1 else "MEDIUM",
                risk_level="LOW"
            ))

        if not proposals:
            pid = f"prop_{uuid.uuid4().hex[:6]}"
            proposals.append(ImprovementProposal(
                proposal_id=pid,
                problem="Python code review accuracy 70%",
                proposed_solution="Integrate Ruff MCP linter & AST analyzer",
                priority="HIGH",
                risk_level="LOW"
            ))

        return proposals
