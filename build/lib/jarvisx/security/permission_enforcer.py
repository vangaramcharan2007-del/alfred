"""Permission Enforcer and Multi-Factor Risk Scoring for Phase 99."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from jarvisx.security.models import (
    PermissionScope,
    RiskBreakdown,
    RiskLevel,
    TrustDecision,
)
from jarvisx.security.security_memory import SecurityMemory


class PermissionEnforcer:
    """Evaluates multi-factor risk scores (0-100) and enforces capability scopes under default-deny policy."""

    def __init__(self, memory: Optional[SecurityMemory] = None):
        self.memory = memory or SecurityMemory()
        self.agent_capabilities = {
            "ResearchAgent": [PermissionScope.FILESYSTEM_READ, PermissionScope.NETWORK_ACCESS],
            "CodingAgent": [PermissionScope.FILESYSTEM_READ, PermissionScope.FILESYSTEM_WRITE_PROJECT],
            "FridayTacticalAgent": [PermissionScope.FILESYSTEM_READ, PermissionScope.FILESYSTEM_WRITE_PROJECT, PermissionScope.TERMINAL_EXECUTE],
            "AlfredMaster": [PermissionScope.FILESYSTEM_READ],
        }

    def compute_risk_score(
        self,
        base_action_risk: int,
        data_sensitivity: int,
        privilege_level: int,
        blast_radius: int,
        irreversibility: int
    ) -> RiskBreakdown:
        return RiskBreakdown(
            base_action_risk=base_action_risk,
            data_sensitivity=data_sensitivity,
            privilege_level=privilege_level,
            blast_radius=blast_radius,
            irreversibility=irreversibility
        )

    def evaluate_action(
        self,
        actor: str,
        action_name: str,
        required_scope: PermissionScope,
        risk_breakdown: Optional[RiskBreakdown] = None
    ) -> TrustDecision:
        """Evaluate if an action is permitted under capability bounds and risk scoring."""
        # 1. Capability Permission Check
        allowed_scopes = self.agent_capabilities.get(actor, [])
        if required_scope not in allowed_scopes:
            return TrustDecision(
                allowed=False,
                risk_score=95,
                risk_level=RiskLevel.CRITICAL,
                reason=f"Permission Escalation Denied: '{actor}' does not possess capability scope '{required_scope.value}'",
                required_scope=required_scope,
                approval_required=True
            )

        # 2. Multi-Factor Risk Calculation
        breakdown = risk_breakdown or RiskBreakdown(15, 0, 5, 0, 0)
        score = breakdown.total_score

        if score < 30:
            level = RiskLevel.LOW
            allowed = True
            appr = False
            reason = f"Low risk action ({score}/100) auto-approved within capability '{required_scope.value}'"
        elif score < 70:
            level = RiskLevel.MODERATE
            allowed = True
            appr = False
            reason = f"Moderate risk action ({score}/100) logged and approved under sandbox guardrails"
        elif score < 90:
            level = RiskLevel.HIGH
            allowed = False
            appr = True
            reason = f"High risk action ({score}/100) requires explicit user confirmation"
        else:
            level = RiskLevel.CRITICAL
            allowed = False
            appr = True
            reason = f"Critical risk action ({score}/100) default blocked by safety policy"

        return TrustDecision(
            allowed=allowed,
            risk_score=score,
            risk_level=level,
            reason=reason,
            required_scope=required_scope,
            approval_required=appr
        )
