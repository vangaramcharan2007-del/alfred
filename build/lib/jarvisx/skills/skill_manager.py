"""Master Controller for Phase 92 Autonomous Skill Acquisition."""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.agents.capability_registry import AutonomousCapabilityRegistry
from jarvisx.skills.gap_detector import CapabilityGapDetector
from jarvisx.skills.models import CapabilityGap, SkillMetadata, SkillStatus
from jarvisx.skills.skill_discovery import SkillDiscoveryEngine
from jarvisx.skills.skill_loader import SkillLoader
from jarvisx.skills.skill_registry import PersistentSkillRegistry
from jarvisx.skills.skill_sandbox import SkillSandbox
from jarvisx.skills.skill_synthesizer import SkillSynthesizer
from jarvisx.skills.skill_validator import SkillValidator


class PersistentSkillManager:
    """End-to-End Autonomous Skill Evolution Engine.
    Detects gaps -> Searches alternatives -> Synthesizes code -> Sandbox tests -> Policy validates -> Registers persistently.
    """

    def __init__(self, capability_registry: Optional[AutonomousCapabilityRegistry] = None):
        self.capability_registry = capability_registry or AutonomousCapabilityRegistry()
        self.gap_detector = CapabilityGapDetector(self.capability_registry)
        self.discovery = SkillDiscoveryEngine(self.capability_registry)
        self.synthesizer = SkillSynthesizer()
        self.sandbox = SkillSandbox()
        self.validator = SkillValidator()
        self.persistent_registry = PersistentSkillRegistry()
        self.loader = SkillLoader()
        
        self.total_acquisitions_attempted = 0
        self.successful_acquisitions = 0
        self._load_existing_persistent_skills()

    def _load_existing_persistent_skills(self) -> None:
        """Automatically load previously acquired skills into active memory on startup."""
        for skill_dict in self.persistent_registry.list_installed_skills():
            meta = self.persistent_registry.get_skill_metadata(skill_dict["name"])
            if meta and meta.status == SkillStatus.INSTALLED:
                cap = self.loader.load_capability(meta)
                if cap:
                    self.capability_registry.register(cap)

    def has_skill(self, name: str) -> bool:
        """Check if skill is actively loaded in memory."""
        return self.capability_registry.get(name) is not None

    def acquire_skill_for_goal(self, goal: str) -> Dict[str, Any]:
        """Execute full autonomous skill acquisition pipeline if a gap is detected."""
        gap = self.gap_detector.detect_gap(goal)
        if not gap:
            return {"status": "NO_GAP_DETECTED", "goal": goal}

        self.total_acquisitions_attempted += 1
        print(f"\n[Skill Evolution]: Missing Capability Gap Detected: '{gap.required_capability}'")
        print(f"  Reason: {gap.reason}")

        # 1. Search existing / packages
        discovery_res = self.discovery.discover_source_for_gap(gap)
        print(f"  Discovery Source: {discovery_res['source_type']} ({discovery_res['details']})")

        # 2. Synthesize new skill
        metadata = self.synthesizer.synthesize_skill(gap, version="v1")
        print(f"  Synthesized: {metadata.file_path}")

        # 3. Sandbox Testing
        sandbox_res = self.sandbox.run_sandbox_test(metadata)
        if not sandbox_res.passed:
            print(f"  [-] Sandbox Test Failed: {sandbox_res.error}")
            return {
                "status": "REJECTED",
                "reason": sandbox_res.error,
                "capability": gap.required_capability,
                "metadata": metadata.to_dict()
            }

        # 4. Policy Validation
        val_res = self.validator.validate_skill_metadata(metadata, sandbox_res)
        if not val_res["approved"]:
            print(f"  [-] Policy Validation Rejected: {val_res['reason']}")
            return {
                "status": "REJECTED",
                "reason": val_res["reason"],
                "capability": gap.required_capability,
                "metadata": metadata.to_dict()
            }

        # 5. Persistent Installation
        self.persistent_registry.register_installed_skill(metadata)
        cap = self.loader.load_capability(metadata)
        if cap:
            self.capability_registry.register(cap)

        self.successful_acquisitions += 1
        print(f"  [+] Skill '{gap.required_capability}' Validated & Installed into Production Registry!")

        return {
            "status": "ACQUIRED_AND_INSTALLED",
            "capability_name": gap.required_capability,
            "version": metadata.version,
            "sasr": round(self.successful_acquisitions / max(self.total_acquisitions_attempted, 1), 2),
            "metadata": metadata.to_dict()
        }
