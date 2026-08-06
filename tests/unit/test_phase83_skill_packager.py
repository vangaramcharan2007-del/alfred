"""Unit and Integration Tests for Phase 83: Autonomous Skill Synthesis & Tool Auto-Packaging Engine.

Tests SkillPackagerEngine skill packaging, file creation in var/skills/, and kernel objectives.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.skills import SkillPackagerEngine


def test_skill_packager_engine_file_generation():
    """Verify SkillPackagerEngine creates persistent SKILL.md definition and indexes metadata."""
    kernel = PersonalOSKernel()
    engine = SkillPackagerEngine(skills_dir="var/test_skills")

    res = engine.package_workflow_into_skill(
        skill_name="Test Automation Routine",
        workflow_steps=["clean pc", "organize downloads", "render companion hud"],
        description="Test workflow packaging routine."
    )

    assert res["status"] == "PACKAGED"
    assert res["skill_name"] == "test_automation_routine"
    assert os.path.exists(res["skill_file"])
    assert res["skills_hspw"] >= 15.0


def test_kernel_objective_routing_phase83():
    """Verify PersonalOSKernel routes skill packaging objectives."""
    kernel = PersonalOSKernel()

    res = kernel.execute_objective(
        "package skill",
        name="System Hygiene Routine",
        steps=["scan storage bloat", "minimize non productive apps"]
    )
    assert res["status"] == "PACKAGED"
    assert res["steps_count"] == 2
