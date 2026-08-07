"""Unit Tests for Phase 92 Autonomous Skill Acquisition."""

import pytest
import shutil
from pathlib import Path
from jarvisx.agents.capability_registry import AutonomousCapabilityRegistry
from jarvisx.skills.gap_detector import CapabilityGapDetector
from jarvisx.skills.models import CapabilityGap, SkillStatus
from jarvisx.skills.skill_discovery import SkillDiscoveryEngine
from jarvisx.skills.skill_manager import PersistentSkillManager
from jarvisx.skills.skill_registry import PersistentSkillRegistry
from jarvisx.skills.skill_sandbox import SkillSandbox
from jarvisx.skills.skill_synthesizer import SkillSynthesizer
from jarvisx.skills.skill_validator import SkillValidator


def test_gap_detector():
    registry = AutonomousCapabilityRegistry()
    detector = CapabilityGapDetector(registry)

    # Goal requiring OCR
    gap = detector.detect_gap("Convert handwritten notes into flashcards")
    assert gap is not None
    assert gap.required_capability == "ocr_flashcard_skill"

    # Goal with existing capability
    gap_none = detector.detect_gap("Create a Python calculator project")
    assert gap_none is None


def test_skill_discovery():
    registry = AutonomousCapabilityRegistry()
    discovery = SkillDiscoveryEngine(registry)

    gap = CapabilityGap(required_capability="ocr_flashcard_skill", reason="Missing OCR")
    res = discovery.discover_source_for_gap(gap)
    assert res["source_type"] in ("INSTALLED_PACKAGE", "SYNTHESIZE_ADAPTER")


def test_skill_synthesizer_and_sandbox_pass():
    synth = SkillSynthesizer(base_skills_dir="var/test_skills")
    sandbox = SkillSandbox()
    validator = SkillValidator()

    gap = CapabilityGap(required_capability="ocr_flashcard_skill", reason="Missing OCR")
    meta = synth.synthesize_skill(gap, version="v1")
    assert Path(meta.file_path).exists()

    # Run sandbox test
    sb_res = sandbox.run_sandbox_test(meta)
    assert sb_res.passed is True
    assert sb_res.status == SkillStatus.VALIDATED

    # Validate policy
    val_res = validator.validate_skill_metadata(meta, sb_res)
    assert val_res["approved"] is True


def test_skill_sandbox_rejects_unsafe_corrupted_format():
    synth = SkillSynthesizer(base_skills_dir="var/test_skills")
    sandbox = SkillSandbox()

    gap = CapabilityGap(required_capability="unknown_corrupted_format", reason="Corrupted binary")
    meta = synth.synthesize_skill(gap, version="v1")

    # Run sandbox test - should fail
    sb_res = sandbox.run_sandbox_test(meta)
    assert sb_res.passed is False
    assert sb_res.status == SkillStatus.REJECTED


def test_persistent_skill_registry_and_restart():
    registry_file = "var/test_skills/test_catalog.json"
    if Path(registry_file).exists():
        Path(registry_file).unlink()

    manager = PersistentSkillManager()
    res = manager.acquire_skill_for_goal("Convert handwritten notes into flashcards")
    assert res["status"] == "ACQUIRED_AND_INSTALLED"
    assert manager.has_skill("ocr_flashcard_skill") is True

    # Simulate restart by creating new manager instance
    new_manager = PersistentSkillManager()
    assert new_manager.has_skill("ocr_flashcard_skill") is True


def test_existing_skill_reuse():
    manager = PersistentSkillManager()
    # First acquisition
    res1 = manager.acquire_skill_for_goal("Convert handwritten notes into flashcards")
    # Second invocation - should detect gap is now closed or existing
    gap = manager.gap_detector.detect_gap("Convert handwritten notes into flashcards")
    assert gap is None  # Gap is closed because capability now exists!
