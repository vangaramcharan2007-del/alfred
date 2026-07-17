from typing import List, Dict, Any, Optional
from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.initiative_manager import ObjectiveProposal, ApprovalMode

class MissionContinuityManager:
    """Detects interrupted objectives and generates recovery proposals."""

    def __init__(self, objective_store: ObjectiveStore):
        self.store = objective_store

    def detect_interrupted_work(self) -> List[Dict[str, Any]]:
        """Find objectives that were active but are now interrupted (e.g., from process restart)."""
        active_objectives = self.store.load_active_objectives()
        interrupted = []
        
        for obj in active_objectives:
            # If the process restarted, everything active is technically interrupted.
            if obj.get("status") in ["IN_PROGRESS", "PENDING", "INTERRUPTED"]:
                # Ensure status reflects interrupted
                if obj.get("status") != "INTERRUPTED":
                    self.store.update_objective(obj["objective_id"], {"status": "INTERRUPTED"})
                    obj["status"] = "INTERRUPTED"
                interrupted.append(obj)
                
        return interrupted

    def recommend_next_step(self, objective: Dict[str, Any]) -> str:
        """Determine what the user should do next based on the objective state."""
        remaining = objective.get("remaining_tasks", [])
        if remaining:
            # Make a human-readable recommendation
            task = remaining[0]
            action = task.replace("_", " ")
            return f"Resume {action}."
        return "Verify completion."

    def generate_recovery_proposals(self) -> List[ObjectiveProposal]:
        """Convert interrupted objectives into recovery proposals."""
        interrupted = self.detect_interrupted_work()
        proposals = []
        
        for obj in interrupted:
            next_step = self.recommend_next_step(obj)
            
            proposal = ObjectiveProposal(
                title=obj.get("title", "Unknown Objective"),
                description=f"Recovered Objective. Progress: {obj.get('progress', 0)}%. Recommended action: {next_step}",
                priority="CRITICAL",  # Recovery is usually high priority
                urgency="IMMEDIATE",
                confidence=100,       # Known exact state
                estimated_value="Mission continuity",
                approval_mode=ApprovalMode.AUTO,
                action_type="recover",
                action_resource=obj["objective_id"]
            )
            proposals.append(proposal)
            
        return proposals
