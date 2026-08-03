from __future__ import annotations
from typing import Dict, Any, Optional

class ApprovalGate:
    """
    Evaluates risk and determines approval mode:
    - LOW: Automatic execution
    - MEDIUM: Confirmation flag
    - HIGH: Explicit approval required
    """
    def check_approval(self, risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        risk_level = risk_assessment.get("risk_level", "LOW")

        if risk_level == "LOW":
            return {
                "approval_granted": True,
                "mode": "AUTOMATIC",
                "message": "Low risk task. Automatic execution approved."
            }
        elif risk_level == "MEDIUM":
            return {
                "approval_granted": True,
                "mode": "CONFIRMATION_CHECK",
                "message": "Medium risk task. Proceeding with confirmation check."
            }
        else:
            return {
                "approval_granted": False,
                "mode": "EXPLICIT_APPROVAL_REQUIRED",
                "message": "High risk task. Requires explicit human approval before proceeding."
            }
