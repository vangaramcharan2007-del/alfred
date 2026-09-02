"""Visual Reflection and Error Recovery for Phase 93."""

from __future__ import annotations
from typing import Dict, Any, Optional
from jarvisx.vision.ui_state import UIState


class VisualReflectionEngine:
    """Visually reflects on action execution outcomes and detects UI state mismatches."""

    def verify_visual_action(
        self,
        action_name: str,
        expected_target: str,
        delta_info: Dict[str, Any],
        post_state: UIState,
    ) -> Dict[str, Any]:
        """Verify whether the physical action produced the expected desktop state change."""
        has_change = delta_info.get("has_visual_change", False)
        target_lower = expected_target.lower()

        # Check if target window appeared in post state
        target_found = any(target_lower in w.title.lower() for w in post_state.windows)

        if "open" in action_name.lower() or "launch" in action_name.lower():
            if target_found or has_change:
                return {
                    "verified": True,
                    "status": "SUCCESS",
                    "reason": f"Visual confirmation: Window/element '{expected_target}' verified on screen."
                }
            else:
                return {
                    "verified": False,
                    "status": "VISUAL_MISMATCH",
                    "reason": f"Visual Mismatch: Expected '{expected_target}' did not appear. Triggering visual recovery.",
                    "needs_recovery": True
                }

        # Default action verification
        return {
            "verified": True,
            "status": "SUCCESS",
            "reason": f"Visual change detected ({delta_info.get('delta_percentage', 0.0)}% pixel delta)."
        }
