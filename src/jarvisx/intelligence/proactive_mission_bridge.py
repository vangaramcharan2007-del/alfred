"""Proactive Mission Bridge for Jarvis X (Layer 2 - Intelligence).

Converts proactive intelligence suggestions into structured Mission objects.
"""

from typing import Any, Dict, Optional

from jarvisx.missions.mission import Mission


class ProactiveMissionBridge:
    """Zero-fluff production mission conversion bridge."""

    def convert_suggestion_to_mission(self, suggestion: Dict[str, Any]) -> Mission:
        """Convert proactive suggestion into a canonical structured Mission object."""
        mission_title = suggestion.get("title", "Proactive Task")
        reason = suggestion.get("reason", "Proactive intelligence recommendation")
        priority = suggestion.get("priority", "MEDIUM")
        reward = suggestion.get("reward", "+1.0 HSPW")
        effort = suggestion.get("estimated_effort", "30 mins")

        mission = Mission(
            title=mission_title,
            user_request=suggestion.get("suggestion", mission_title),
            intent="proactive_intelligence",
            capability="proactive_engine",
            status="PENDING",
            context={
                "suggestion_id": suggestion.get("suggestion_id"),
                "reason": reason,
                "priority": priority,
                "reward": reward,
                "estimated_effort": effort,
                "evidence": suggestion.get("evidence", {}),
            },
            evidence=suggestion.get("evidence", {}),
        )

        return mission
