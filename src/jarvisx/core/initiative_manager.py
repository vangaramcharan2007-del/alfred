# src/jarvisx/core/initiative_manager.py

import uuid
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from jarvisx.core.world_state_monitor import WorldEvent

class ProposalStatus(str, Enum):
    PENDING = "PENDING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    APPROVED = "APPROVED"
    DISPATCHED = "DISPATCHED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    VERIFIED = "VERIFIED"

class ApprovalMode(str, Enum):
    MANUAL = "MANUAL"
    AUTO = "AUTO"
    SCHEDULED = "SCHEDULED"

@dataclass
class ObjectiveProposal:
    title: str
    description: str
    priority: str
    urgency: str
    confidence: int
    estimated_value: str
    approval_mode: ApprovalMode
    action_type: str
    action_resource: str
    id: str = field(default_factory=lambda: "obj_" + uuid.uuid4().hex[:8])
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: float = field(default_factory=time.time)
    risk_score: int = 10
    
class InitiativeManager:
    """
    Evaluates proactive opportunities, scores initiative candidates,
    maintains initiative budgets, and prevents initiative flooding.
    """
    def __init__(self, approval_mode: ApprovalMode = ApprovalMode.AUTO):
        self.proposals: List[ObjectiveProposal] = []
        self.approval_mode = approval_mode

    def handle_world_event(self, event: WorldEvent):
        """Convert a WorldEvent into an ObjectiveProposal."""
        
        if event.event_type == "DOWNLOADS_CLUTTER":
            proposal = ObjectiveProposal(
                title="Clean mock downloads",
                description=f"Detected {event.metadata.get('file_count')} files in {event.metadata.get('path')}",
                priority="MEDIUM",
                urgency="NORMAL",
                confidence=93,
                estimated_value="Reclaim disk space",
                approval_mode=self.approval_mode,
                action_type="clean",
                action_resource=event.metadata.get("path")
            )
        elif event.event_type == "TASK_FAILURE":
            proposal = ObjectiveProposal(
                title="Investigate backup failures",
                description=f"Task {event.metadata.get('task_name')} failed {event.metadata.get('failures')} times",
                priority="HIGH",
                urgency="CRITICAL",
                confidence=85,
                estimated_value="Ensure data safety",
                approval_mode=self.approval_mode,
                action_type="investigate",
                action_resource=event.metadata.get("task_name")
            )
        elif event.event_type == "DISK_PRESSURE":
            proposal = ObjectiveProposal(
                title="Analyze disk usage",
                description=f"Disk usage is at {event.metadata.get('disk_usage')}%",
                priority="CRITICAL",
                urgency="CRITICAL",
                confidence=99,
                estimated_value="Prevent system crash",
                approval_mode=self.approval_mode,
                action_type="analyze",
                action_resource="disk"
            )
        else:
            return

        proposal.status = ProposalStatus.WAITING_APPROVAL
        
        # Deduplicate: Don't add if a pending/approved/dispatched proposal exists for same action_type and resource
        for existing in self.proposals:
            if existing.action_type == proposal.action_type and existing.action_resource == proposal.action_resource:
                if existing.status in [ProposalStatus.PENDING, ProposalStatus.WAITING_APPROVAL, ProposalStatus.APPROVED, ProposalStatus.DISPATCHED]:
                    return
                    
        self.proposals.append(proposal)

    def get_pending_proposals(self) -> List[ObjectiveProposal]:
        return [p for p in self.proposals if p.status == ProposalStatus.WAITING_APPROVAL]

    def approve_proposal(self, proposal_id: str):
        for p in self.proposals:
            if p.id == proposal_id:
                p.status = ProposalStatus.APPROVED
                return True
        return False
        
    def dispatch_proposal(self, proposal_id: str):
        for p in self.proposals:
            if p.id == proposal_id:
                p.status = ProposalStatus.DISPATCHED
                return True
        return False

    def complete_proposal(self, proposal_id: str, success: bool):
        for p in self.proposals:
            if p.id == proposal_id:
                p.status = ProposalStatus.COMPLETED if success else ProposalStatus.FAILED
                return True
        return False
        
    def verify_proposal(self, proposal_id: str):
        for p in self.proposals:
            if p.id == proposal_id:
                p.status = ProposalStatus.VERIFIED
                return True
        return False
