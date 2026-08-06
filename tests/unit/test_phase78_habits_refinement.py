"""Unit and Integration Tests for Phase 78: Autonomous Self-Refinement & Contextual Habit Engine.

Tests ContextualHabitEngine, SelfRefinementEngine, and CompanionHUDController.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.habits import ContextualHabitEngine
from jarvisx.refinement import SelfRefinementEngine
from jarvisx.automation import CompanionHUDController


def test_contextual_habit_engine_pattern_detection():
    """Verify ContextualHabitEngine records activity events and surfaces recurring habits."""
    habit_engine = ContextualHabitEngine()

    habit_engine.record_activity_event("study_algorithms", "Revised Graph Theory")
    habit_engine.record_activity_event("study_algorithms", "Revised Binary Trees")

    habits = habit_engine.detect_habits()
    assert len(habits) >= 1
    assert any("study_algorithms" in h["action_type"] for h in habits)


def test_self_refinement_multiplier_calculation():
    """Verify SelfRefinementEngine calculates planning multipliers from historical feedback."""
    kernel = PersonalOSKernel()
    refinement = kernel.self_refinement

    # Seed feedback record
    kernel.feedback_engine.process_mission_feedback("m_test_01", expected_effort_hours=2.0, actual_effort_hours=3.0)

    params = refinement.compute_refinement_parameters()
    assert params["status"] == "REFINED"
    assert params["estimation_multiplier"] >= 1.0


def test_companion_hud_rendering():
    """Verify CompanionHUDController renders HTML overlay."""
    kernel = PersonalOSKernel()
    hud = CompanionHUDController(hud_path="var/config/test_hud.html")

    res = hud.render_companion_hud(os_kernel=kernel)
    assert res["status"] == "RENDERED"
    assert os.path.exists(res["hud_file"])


def test_kernel_objective_routing_phase78():
    """Verify PersonalOSKernel routes habit, self-refinement, and HUD objectives."""
    kernel = PersonalOSKernel()

    h_res = kernel.execute_objective("detect habit")
    assert h_res["status"] == "completed"
    assert "habits" in h_res

    r_res = kernel.execute_objective("refine strategy")
    assert r_res["status"] in ("REFINED", "nominal")

    hud_res = kernel.execute_objective("render hud")
    assert hud_res["status"] == "RENDERED"
