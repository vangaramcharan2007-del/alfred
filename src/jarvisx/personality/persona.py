from __future__ import annotations
from typing import Dict, Any, Optional

class AlfredPersona:
    """
    Alfred personality formatting engine providing formal, precise, and helpful communication.
    """
    def format_response(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        text_strip = text.strip()
        if text_strip.startswith("Sir,") or text_strip.startswith("Alfred:"):
            return text_strip

        return f"Sir, {text_strip}"

    def format_mission_completion(self, mission_title: str, test_status: str = "PASS") -> str:
        return (
            f"Sir, the implementation for '{mission_title}' has been completed. "
            f"The test suite status is {test_status}. "
            f"I have committed the workspace changes to local version control and generated the intelligence report."
        )
