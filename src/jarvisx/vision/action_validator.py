"""Action Safety Validator for Phase 93 Computer Use & Vision Layer."""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from jarvisx.agents.action_models import PolicyDecision, RiskLevel
from jarvisx.vision.ui_state import UIElement


class ActionSafetyValidator:
    """Validates physical mouse and keyboard action proposals against screen boundaries and safety policy."""

    def __init__(self, screen_bounds: Tuple[int, int] = (1920, 1080)):
        self.max_width, self.max_height = screen_bounds

    def validate_mouse_action(
        self,
        action_type: str,
        target_coords: Tuple[int, int],
        element: Optional[UIElement] = None
    ) -> Dict[str, Any]:
        """Verify mouse coordinates are within physical screen boundaries and safe."""
        x, y = target_coords

        # 1. Screen Boundary Safety Clamping Check
        if not (0 <= x <= self.max_width and 0 <= y <= self.max_height):
            return {
                "decision": PolicyDecision.BLOCK.value,
                "reason": f"Target coordinates ({x}, {y}) out of physical screen bounds ({self.max_width}x{self.max_height})."
            }

        # 2. Risk Level Evaluation
        if element and "delete" in element.label.lower():
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

    def validate_keyboard_action(self, key_text: str) -> Dict[str, Any]:
        """Verify keyboard inputs do not contain dangerous shell sequences."""
        forbidden = ["format c:", "rmdir /s /q", "drop database"]
        for f in forbidden:
            if f in key_text.lower():
                return {
                    "decision": PolicyDecision.BLOCK.value,
                    "reason": f"Forbidden destructive keyboard sequence '{f}' blocked."
                }
        return {
            "decision": PolicyDecision.ALLOW.value,
            "risk": RiskLevel.LOW.value,
            "reason": "Keyboard action validated."
        }
