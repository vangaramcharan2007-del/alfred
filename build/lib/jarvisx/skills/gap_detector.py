"""Capability Gap Detector for Phase 92 Autonomous Skill Acquisition."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.agents.capability_registry import AutonomousCapabilityRegistry
from jarvisx.skills.models import CapabilityGap


class CapabilityGapDetector:
    """Analyzes user missions against available capabilities to identify missing tool requirements."""

    def __init__(self, capability_registry: Optional[AutonomousCapabilityRegistry] = None):
        self.registry = capability_registry or AutonomousCapabilityRegistry()

    def detect_gap(self, goal: str) -> Optional[CapabilityGap]:
        """Detect if the mission goal requires a capability currently missing from the registry."""
        g = goal.lower().strip()

        # 1. OCR & Handwritten Notes to Flashcards Gap
        if "ocr" in g or "handwriting" in g or "handwritten" in g or "flashcard" in g:
            if not self.registry.get("image_to_text") and not self.registry.get("ocr_flashcard_skill"):
                return CapabilityGap(
                    required_capability="ocr_flashcard_skill",
                    reason="No Optical Character Recognition (OCR) or handwriting flashcard synthesizer available in registry.",
                    confidence=0.95,
                    suggested_inputs=["input_source", "output_dir"],
                    suggested_category="vision_education"
                )

        # 2. Corrupted / Unknown File Format Gap
        elif "unknown" in g and ("format" in g or "file" in g or "corrupted" in g):
            return CapabilityGap(
                required_capability="unknown_format_parser",
                reason="No parser available for proprietary or corrupted binary structure.",
                confidence=0.88,
                suggested_inputs=["file_path"],
                suggested_category="binary_analysis"
            )

        # 3. Audio & Speech Transcription Gap
        elif "transcribe" in g or "audio" in g or "podcast" in g:
            if not self.registry.get("audio_transcription_skill"):
                return CapabilityGap(
                    required_capability="audio_transcription_skill",
                    reason="No audio speech-to-text transcription engine available in registry.",
                    confidence=0.90,
                    suggested_inputs=["audio_path"],
                    suggested_category="multimedia"
                )

        # 4. QR Code Generator Gap
        elif "qr code" in g or "qr_code" in g:
            if not self.registry.get("qr_code_generator"):
                return CapabilityGap(
                    required_capability="qr_code_generator",
                    reason="No QR matrix encoder available in registry.",
                    confidence=0.92,
                    suggested_inputs=["data", "output_path"],
                    suggested_category="utility"
                )

        return None
