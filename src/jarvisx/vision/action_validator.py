"""Action Safety Validator for Phase 93 Computer Use & Vision Layer."""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from jarvisx.agents.action_models import PolicyDecision, RiskLevel
from jarvisx.vision.ui_state import UIElement


class ActionSafetyValidator:
    """Validates physical mouse and keyboard action proposals against screen boundaries and safety policy."""

    def __init__(self, screen_bounds: Tuple[int, int] = (1920, 1080)):
        self.max_width, self.max_height = screen_bounds

    DANGEROUS_TARGET_KEYWORDS = [
        "password", "passwd", "pin", "credential", "uac", "wallet",
        "payment", "credit card", "cvv", "security dialog", "authenticator", "api key", "secret"
    ]

    def validate_window_safety(self, window_title: str) -> Dict[str, Any]:
        """Verify window is safe to interact with and not a security/payment/credential prompt."""
        title_lower = window_title.lower()
        for kw in self.DANGEROUS_TARGET_KEYWORDS:
            if kw in title_lower:
                return {
                    "decision": PolicyDecision.BLOCK.value,
                    "reason": f"Target window '{window_title}' contains sensitive/security keyword '{kw}'. Automated interaction blocked."
                }
        return {
            "decision": PolicyDecision.ALLOW.value,
            "risk": RiskLevel.LOW.value,
            "reason": "Window safe for automation."
        }

    def validate_mouse_action(
        self,
        action_type: str,
        target_coords: Tuple[int, int],
        element: Optional[UIElement] = None,
        active_window: str = "",
    ) -> Dict[str, Any]:
        """Verify mouse coordinates are within physical screen boundaries and safe."""
        # 0. Check active window safety
        if active_window:
            win_check = self.validate_window_safety(active_window)
            if win_check["decision"] == PolicyDecision.BLOCK.value:
                return win_check

        x, y = target_coords

        # 1. Screen Boundary Safety Clamping Check
        if not (0 <= x <= self.max_width and 0 <= y <= self.max_height):
            return {
                "decision": PolicyDecision.BLOCK.value,
                "reason": f"Target coordinates ({x}, {y}) out of physical screen bounds ({self.max_width}x{self.max_height})."
            }

        # 2. Sensitive Element Keywords Check
        if element:
            el_lower = element.label.lower()
            for kw in self.DANGEROUS_TARGET_KEYWORDS:
                if kw in el_lower:
                    return {
                        "decision": PolicyDecision.BLOCK.value,
                        "reason": f"Target element '{element.label}' contains sensitive keyword '{kw}'. Interaction blocked."
                    }
            if "delete" in el_lower:
                return {
                    "decision": PolicyDecision.ASK_USER.value,
                    "risk": RiskLevel.HIGH.value,
                    "reason": f"Target '{element.label}' carries destructive risk and requires user authorization."
                }

        return {
            "decision": PolicyDecision.ALLOW.value,
            "risk": RiskLevel.LOW.value,
            "reason": "Action validated within safe desktop boundaries."
        }

    def validate_keyboard_action(self, key_text: str, active_window: str = "") -> Dict[str, Any]:
        """Verify keyboard inputs do not contain dangerous shell sequences or credentials."""
        # 0. Check active window safety
        if active_window:
            win_check = self.validate_window_safety(active_window)
            if win_check["decision"] == PolicyDecision.BLOCK.value:
                return win_check

        forbidden = ["format c:", "rmdir /s /q", "drop database", "del /f /s /q"]
        for f in forbidden:
            if f in key_text.lower():
                return {
                    "decision": PolicyDecision.BLOCK.value,
                    "reason": f"Forbidden destructive keyboard sequence '{f}' blocked."
                }

        for kw in self.DANGEROUS_TARGET_KEYWORDS:
            if kw in key_text.lower() and len(key_text) > 15:
                return {
                    "decision": PolicyDecision.BLOCK.value,
                    "reason": f"Potential credential payload containing '{kw}' blocked."
                }

        return {
            "decision": PolicyDecision.ALLOW.value,
            "risk": RiskLevel.LOW.value,
            "reason": "Keyboard action validated."
        }
