"""
Real Screen Analyzer for Desktop Vision Intelligence.
Combines window captures with context detection and traceback error scanning.
"""
from __future__ import annotations
import re
from typing import Dict, Any, Optional
from jarvisx.presence.vision.screen_capture import ScreenCaptureEngine
from jarvisx.presence.vision.context_detector import DesktopContextDetector


class ScreenAnalyzer:
    """
    Analyzes visual screen state, extracts error text, and provides vision summaries.
    """

    def __init__(
        self,
        capture_engine: Optional[ScreenCaptureEngine] = None,
        context_detector: Optional[DesktopContextDetector] = None
    ):
        self.capture_engine = capture_engine or ScreenCaptureEngine()
        self.context_detector = context_detector or DesktopContextDetector()

    def analyze_screen(self) -> Dict[str, Any]:
        snapshot = self.capture_engine.capture_active_window()
        ctx = self.context_detector.detect_context(snapshot["active_window"])

        return {
            "status": "ANALYZED",
            "snapshot": snapshot,
            "context": ctx,
            "vision_summary": f"Active {ctx['application_type']} window '{ctx['active_window']}' detected.",
            "suggested_fix_action": "alfred_fix_this" if ctx.get("has_error") else None
        }
