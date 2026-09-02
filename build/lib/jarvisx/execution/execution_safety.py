"""Execution Safety Guard for Jarvis X (Layer 3 - Execution).

Enforces confidence thresholds, capability reality checks, risk level assessment,
and explicit confirmation before executing destructive, external communication, or financial actions.
"""

from typing import Any, Dict, Optional

from jarvisx.automation.capability_registry import CapabilityRealityRegistry


class ExecutionSafetyGuard:
    """Zero-fluff production execution safety guard layer."""

    DESTRUCTIVE_KEYWORDS = ["delete file", "format disk", "drop table", "purge system", "rm -rf"]
    COMMUNICATION_KEYWORDS = ["send message", "send email", "post update", "slack notify"]
    FINANCIAL_KEYWORDS = ["pay bill", "transfer money", "buy", "purchase", "credit card"]

    def __init__(self, capability_registry: Optional[CapabilityRealityRegistry] = None, min_confidence: float = 0.70):
        self.capability_registry = capability_registry or CapabilityRealityRegistry()
        self.min_confidence = min_confidence

    def evaluate_execution_safety(
        self,
        mission_title: str,
        confidence: float = 0.85,
        user_confirmed: bool = False,
    ) -> Dict[str, Any]:
        """Evaluate mission safety prior to execution."""
        t_lower = mission_title.lower()

        # 1. Check confidence threshold
        if confidence < self.min_confidence:
            return {
                "permitted": False,
                "risk_level": "HIGH",
                "status": "BLOCKED_LOW_CONFIDENCE",
                "reason": f"Execution confidence ({confidence:.2f}) below threshold ({self.min_confidence:.2f}).",
            }

        # 2. Check destructive actions
        if any(kw in t_lower for kw in self.DESTRUCTIVE_KEYWORDS):
            if not user_confirmed:
                return {
                    "permitted": False,
                    "risk_level": "CRITICAL",
                    "status": "REQUIRES_USER_CONFIRMATION",
                    "reason": f"Mission '{mission_title}' involves destructive action and requires explicit user confirmation.",
                }

        # 3. Check external communication actions
        if any(kw in t_lower for kw in self.COMMUNICATION_KEYWORDS):
            if not user_confirmed:
                return {
                    "permitted": False,
                    "risk_level": "MEDIUM",
                    "status": "REQUIRES_USER_CONFIRMATION",
                    "reason": f"Mission '{mission_title}' involves external communication and requires user confirmation.",
                }

        # 4. Check financial actions
        if any(kw in t_lower for kw in self.FINANCIAL_KEYWORDS):
            if not user_confirmed:
                return {
                    "permitted": False,
                    "risk_level": "CRITICAL",
                    "status": "REQUIRES_USER_CONFIRMATION",
                    "reason": f"Mission '{mission_title}' involves financial transaction and requires explicit user confirmation.",
                }

        # 5. Check capability reality registry
        cap_res = self.capability_registry.verify_capability(mission_title)
        if not cap_res["verified"] and cap_res["capability"]["execution_type"] == "UNKNOWN":
            return {
                "permitted": False,
                "risk_level": "HIGH",
                "status": "BLOCKED_UNKNOWN_CAPABILITY",
                "reason": cap_res["reason"],
            }

        return {
            "permitted": True,
            "risk_level": "LOW",
            "status": "PERMITTED",
            "reason": "Mission passed all execution safety and confirmation checks.",
        }
