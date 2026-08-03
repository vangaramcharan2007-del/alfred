"""
Risk & Security Gate for Desktop Computer Automation.
Categorizes actions into LOW, MEDIUM, HIGH, and CRITICAL risk scores.
Enforces permission checks and explicit user confirmation for high-risk actions.
"""
from __future__ import annotations
from typing import Dict, Any, Optional


class RiskSecurityGate:
    """
    Evaluates action risk level and handles permission checking.
    """

    HIGH_RISK_KEYWORDS = ["delete", "remove", "kill", "format", "shutdown", "uninstall", "force"]
    MEDIUM_RISK_KEYWORDS = ["compress", "organize", "rename", "push", "commit", "lock"]

    def evaluate_risk(self, action_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        act_lower = action_id.lower()
        ctx_str = str(context or {}).lower()

        if any(k in act_lower or k in ctx_str for k in self.HIGH_RISK_KEYWORDS):
            level = "HIGH"
            requires_confirmation = True
            score = 0.85
        elif any(k in act_lower or k in ctx_str for k in self.MEDIUM_RISK_KEYWORDS):
            level = "MEDIUM"
            requires_confirmation = False
            score = 0.45
        else:
            level = "LOW"
            requires_confirmation = False
            score = 0.10

        return {
            "action_id": action_id,
            "risk_level": level,
            "risk_score": score,
            "requires_confirmation": requires_confirmation
        }

    def check_permission(self, action_id: str, context: Optional[Dict[str, Any]] = None, confirmed: bool = False) -> Dict[str, Any]:
        risk = self.evaluate_risk(action_id, context)
        if risk["requires_confirmation"] and not confirmed:
            return {
                "allowed": False,
                "status": "CONFIRMATION_REQUIRED",
                "reason": f"Action '{action_id}' is rated {risk['risk_level']} risk and requires explicit user confirmation.",
                "risk": risk
            }
        return {
            "allowed": True,
            "status": "PERMISSION_GRANTED",
            "risk": risk
        }
