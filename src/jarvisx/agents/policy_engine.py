"""Deterministic Policy Engine & Safety Gate for Phase 91 Autonomous Mission Brain."""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional
from jarvisx.agents.action_models import ActionProposal, Capability, PolicyDecision, RiskLevel


class PolicyEngine:
    """Deterministic safety gate and security policy validator for agent actions."""

    FORBIDDEN_PATHS = [
        r"c:\windows",
        r"c:\program files",
        r"c:\program files (x86)",
        r"/system",
        r"/etc",
    ]

    def __init__(self, allow_high_risk: bool = True):
        self.allow_high_risk = allow_high_risk

    def evaluate_proposal(self, proposal: ActionProposal, capability: Optional[Capability] = None) -> Dict[str, Any]:
        """Deterministically validate an action proposal against safety policy."""
        # 1. Capability presence check
        if not capability:
            return {
                "decision": PolicyDecision.BLOCK.value,
                "reason": f"Capability '{proposal.capability_name}' not found in registry."
            }

        # 2. Risk Level Evaluation
        if capability.risk_level == RiskLevel.CRITICAL:
            return {
                "decision": PolicyDecision.BLOCK.value,
                "reason": f"Action '{proposal.capability_name}' exceeds critical safety risk threshold."
            }

        # 3. Path Security Check for Filesystem Actions
        target_path = str(proposal.arguments.get("target_path", "") or proposal.arguments.get("target_root", "") or proposal.arguments.get("output_dir", "")).lower()
        if target_path:
            for forbidden in self.FORBIDDEN_PATHS:
                if target_path.startswith(forbidden):
                    return {
                        "decision": PolicyDecision.BLOCK.value,
                        "reason": f"Access to system protected directory '{forbidden}' is strictly blocked."
                    }

        # 4. Confirmation policy for HIGH risk actions
        if capability.risk_level == RiskLevel.HIGH and not self.allow_high_risk:
            return {
                "decision": PolicyDecision.ASK_USER.value,
                "reason": f"Action '{proposal.capability_name}' requires explicit user confirmation."
            }

        # 5. Default Allow for validated actions
        return {
            "decision": PolicyDecision.ALLOW.value,
            "risk": capability.risk_level.value,
            "permissions": capability.permissions,
            "reason": "Policy check passed."
        }
