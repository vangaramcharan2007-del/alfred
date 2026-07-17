from typing import Any
from jarvisx.core.initiative_manager import InitiativeManager, ObjectiveProposal, ApprovalMode

class ImprovementEngine:
    """Owns proposal generation for capability evolution."""
    
    def __init__(self, initiative_manager: InitiativeManager):
        self.initiative_manager = initiative_manager
        
    def generate_improvement_proposal(self, capability_gap: str) -> ObjectiveProposal:
        """Generate capability proposals."""
        title = f"Create {capability_gap} skill"
        description = f"Proposal:\n{title}\n\nPriority:\nHIGH\n\nConfidence:\n94%"
        
        proposal = ObjectiveProposal(
            title=title,
            description=description,
            priority="HIGH",
            urgency="IMMEDIATE",
            confidence=94,
            estimated_value="High",
            approval_mode=ApprovalMode.AUTO,
            action_type="capability_evolution",
            action_resource=capability_gap
        )
        return proposal
        
    def submit_proposal(self, proposal: ObjectiveProposal):
        """Submit proposals to InitiativeManager."""
        self.initiative_manager.proposals.append(proposal)
