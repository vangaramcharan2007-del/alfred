from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.evolution.improvement_detector import ImprovementProposal

@dataclass
class EvolutionMission:
    mission_id: str
    proposal_id: str
    title: str
    target_component: str
    steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "proposal_id": self.proposal_id,
            "title": self.title,
            "target_component": self.target_component,
            "steps": self.steps
        }

class EvolutionPlanner:
    def create_mission(self, proposal: ImprovementProposal) -> EvolutionMission:
        mid = f"ev_mission_{proposal.proposal_id}"
        steps = [
            f"Phase 1: Research & analyze solution for '{proposal.problem}'",
            f"Phase 2: Generate system architecture plan for {proposal.proposed_solution}",
            "Phase 3: Apply code modifications in sandbox environment",
            "Phase 4: Run unit test suite and safety checks",
            "Phase 5: Commit changes to Git & update evolution memory"
        ]
        return EvolutionMission(
            mission_id=mid,
            proposal_id=proposal.proposal_id,
            title=proposal.proposed_solution,
            target_component="jarvisx_core",
            steps=steps
        )
