"""Proactive Safety Guard for Jarvis X (Layer 2 - Intelligence).

Enforces confidence threshold (>= 0.70), capability reality verification,
and explicit user confirmation before executing impactful proactive actions.
"""

from typing import Any, Dict, Optional

from jarvisx.automation.capability_registry import CapabilityRealityRegistry


class ProactiveSafetyGuard:
    """Zero-fluff production proactive safety evaluation layer."""

    IMPACTFUL_KEYWORDS = [
        "send message",
        "delete file",
        "modify system",
        "format disk",
        "drop table",
        "push git",
        "shutdown",
    ]

    def __init__(self, capability_registry: Optional[CapabilityRealityRegistry] = None, min_confidence: float = 0.70):
        self.capability_registry = capability_registry or CapabilityRealityRegistry()
        self.min_confidence = min_confidence

    def evaluate_proactive_safety(self, suggestion: Dict[str, Any], user_confirmed: bool = False) -> Dict[str, Any]:
        """Evaluate proactive action safety against confidence thresholds, capability reality, and impact rules."""
        conf = suggestion.get("confidence", 0.0)
        title = suggestion.get("title", "").lower()
        text = suggestion.get("suggestion", "").lower()

        # 1. Confidence Threshold Check
        if conf < self.min_confidence:
            return {
                "permitted": False,
                "status": "BLOCKED_LOW_CONFIDENCE",
                "reason": f"Proactive suggestion confidence ({conf:.2f}) is below minimum threshold ({self.min_confidence:.2f}).",
            }

        # 2. Impactful Action Check (Requires explicit user confirmation)
        is_impactful = any(kw in title or kw in text for kw in self.IMPACTFUL_KEYWORDS)
        if is_impactful and not user_confirmed:
            return {
                "permitted": False,
                "status": "REQUIRES_USER_CONFIRMATION",
                "reason": f"Proactive action '{suggestion.get('title')}' is impactful and requires explicit user confirmation.",
            }

        # 3. Capability Reality Verification Check
        target_cap = "system cleaner" if "clean" in title or "storage" in title else (
            "folder watcher" if "organize" in title or "download" in title else (
                "deliverable synthesizer" if "ppt" in title or "poster" in title else "deliverable synthesizer"
            )
        )
        cap_verify = self.capability_registry.verify_capability(target_cap)
        if not cap_verify["verified"] and cap_verify["capability"]["execution_type"] == "UNKNOWN":
            return {
                "permitted": False,
                "status": "BLOCKED_UNKNOWN_CAPABILITY",
                "reason": cap_verify["reason"],
            }

        return {
            "permitted": True,
            "status": "PERMITTED",
            "reason": "Proactive action passed all safety and reality validation checks.",
        }
