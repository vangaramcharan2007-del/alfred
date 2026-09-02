"""Skill Discovery Engine for Phase 92 Autonomous Skill Acquisition."""

from __future__ import annotations
import importlib
import shutil
from typing import Dict, Any, List, Optional
from jarvisx.agents.capability_registry import AutonomousCapabilityRegistry
from jarvisx.skills.models import CapabilityGap, SkillStatus


class SkillDiscoveryEngine:
    """Prioritized discovery hierarchy for missing capabilities.
    Priority:
      1. Existing registered skills
      2. Installed Python packages/modules
      3. System binaries / CLI tools
      4. Generate adapter / synthesis
    """

    def __init__(self, capability_registry: Optional[AutonomousCapabilityRegistry] = None):
        self.registry = capability_registry or AutonomousCapabilityRegistry()

    def discover_source_for_gap(self, gap: CapabilityGap) -> Dict[str, Any]:
        """Find the best resolution path for a capability gap."""
        cap_name = gap.required_capability

        # Priority 1: Existing registered capability
        if self.registry.get(cap_name):
            return {
                "source_type": "EXISTING_CAPABILITY",
                "capability_name": cap_name,
                "confidence": 1.0,
                "details": "Capability already present in registry."
            }

        # Priority 2: Python packages installed in environment
        pkg_mapping = {
            "ocr_flashcard_skill": "json",
            "image_to_text": "PIL",
            "pdf_summary_skill": "pypdf",
            "audio_transcription_skill": "wave",
        }
        candidate_pkg = pkg_mapping.get(cap_name, cap_name.split("_")[0])
        try:
            importlib.import_module(candidate_pkg)
            return {
                "source_type": "INSTALLED_PACKAGE",
                "package_name": candidate_pkg,
                "capability_name": cap_name,
                "confidence": 0.95,
                "details": f"Discovered installed Python library '{candidate_pkg}' for adapter synthesis."
            }
        except ImportError:
            pass

        # Priority 3: System CLI binaries
        candidate_bin = candidate_pkg
        if shutil.which(candidate_bin):
            return {
                "source_type": "SYSTEM_BINARY",
                "binary_name": candidate_bin,
                "capability_name": cap_name,
                "confidence": 0.90,
                "details": f"Discovered system executable '{candidate_bin}' on PATH."
            }

        # Priority 4: Dynamic Adapter Synthesis
        return {
            "source_type": "SYNTHESIZE_ADAPTER",
            "capability_name": cap_name,
            "confidence": 0.85,
            "details": f"Synthesize custom type-hinted {cap_name} module."
        }
