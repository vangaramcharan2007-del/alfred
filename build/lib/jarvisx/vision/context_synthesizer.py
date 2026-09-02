"""Context-Aware Assistance Synthesizer for Jarvis X (Layer 2 - Intelligence).

Correlates active screen context with user goals and personal knowledge base
to surface proactive assistance payloads.
"""

from typing import Any, Dict, Optional

from jarvisx.vision.screen_context_engine import ScreenContextEngine


class ContextSynthesizer:
    """Zero-fluff production contextual assistance synthesizer."""

    def __init__(self, context_engine: Optional[ScreenContextEngine] = None):
        self.context_engine = context_engine or ScreenContextEngine()

    def generate_contextual_assistance(self, os_kernel: Any) -> Dict[str, Any]:
        """Synthesize relevant assistance based on live screen context."""
        captured = self.context_engine.capture_active_context()
        category = captured.get("context_category", "GENERAL_DESKTOP")

        assistance_map = {
            "CODE_DEVELOPMENT": {
                "recommendation": "Active IDE / Terminal detected. Auto-monitoring build status & git branch.",
                "suggested_action": "run tests",
            },
            "ACADEMIC_STUDY": {
                "recommendation": "Academic slides / lecture material detected. Ready to generate revision flashcards.",
                "suggested_action": "ingest lecture",
            },
            "WEB_RESEARCH": {
                "recommendation": "Browser documentation active. Ready to extract summary keypoints.",
                "suggested_action": "curate docs",
            },
            "GENERAL_DESKTOP": {
                "recommendation": "General desktop activity. Systems nominal.",
                "suggested_action": "show system status",
            },
        }

        assistance = assistance_map.get(category, assistance_map["GENERAL_DESKTOP"])

        return {
            "status": "SYNTHESIZED",
            "active_category": category,
            "assistance": assistance,
            "screen_snapshot": captured,
        }
