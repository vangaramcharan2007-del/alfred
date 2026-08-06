"""Unit and Integration Tests for Phase 76: Adaptive Planning Intelligence Engine.

Tests AdaptivePlanner, ProgressIntelligence, Replanner, Prioritizer, and DailyIntelligenceBriefing.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.planning import AdaptivePlanner, ProgressIntelligence, Replanner, Prioritizer, DailyIntelligenceBriefing


def test_goal_decomposition_into_mission_tree():
    """Verify AdaptivePlanner decomposes goals into structured Mission Trees with dependencies."""
    planner = AdaptivePlanner()
    res = planner.decompose_goal_into_mission_tree("Learn Machine Learning", goal_type="LONG_TERM")

    assert res["status"] == "completed"
    assert res["missions_count"] >= 3
    tree = res["mission_tree"]
    first = tree[0]
    second = tree[1]

    assert "title" in first
    assert "context" in first
    assert "estimated_effort" in first["context"]
    assert "completion_criteria" in first["context"]
    # Verify dependency chain
    assert len(second["context"]["dependencies"]) > 0


def test_progress_intelligence_risk_detection():
    """Verify ProgressIntelligence detects falling_behind, unrealistic_plans, and blocked dependencies."""
    intel = ProgressIntelligence()

    # Seed an incomplete goal with deadline
    intel.goal_tracker.add_goal("Calculus Exam", goal_type="DEADLINE", deadline="Tomorrow 5 PM")

    history = [
        {"objective": "task 1", "outcome": "failed"},
        {"objective": "task 2", "outcome": "failed"},
        {"objective": "task 3", "outcome": "completed"},
    ]

    analysis = intel.analyze_execution_progress(history)
    assert analysis["has_risks"] is True
    risks = [r["risk_type"] for r in analysis["risks_detected"]]
    assert "FALLING_BEHIND" in risks or "UNREALISTIC_PLANS" in risks


def test_dynamic_replanner():
    """Verify Replanner adjusts daily target when reality deviates from plan."""
    kernel = PersonalOSKernel()
    g = kernel.goal_tracker.add_goal("Study Algorithms", goal_type="SHORT_TERM")

    res = kernel.replanner.dynamically_adjust_plan(
        goal_id=g["goal_id"],
        target_hours_per_day=3.0,
        actual_hours_per_day=0.5,
    )

    assert res["status"] == "REPLANNED"
    assert res["adjusted_target_hours"] < 3.0
    assert "consistency" in res["new_next_action"].lower()


def test_prioritizer_scoring_formula():
    """Verify Prioritizer computes priority = deadline_urgency + goal_importance + dependency_impact + user_preference."""
    prioritizer = Prioritizer()
    res = prioritizer.compute_priority_score(
        days_until_deadline=1.0,  # Urgent deadline
        goal_importance=8.0,
        downstream_dependencies_count=2,
        user_preference_weight=2.0,
    )

    assert res["total_score"] >= 15.0
    assert res["priority_label"] == "HIGH"
    assert res["deadline_urgency"] > 5.0
    assert res["dependency_impact"] == 4.0


def test_daily_intelligence_briefing():
    """Verify DailyIntelligenceBriefing synthesizes executive reports with priorities, risks, and recommended missions."""
    kernel = PersonalOSKernel()
    kernel.execute_objective("add goal", goal="Finish Calculus Assignment", type="DEADLINE", deadline="Tomorrow")

    report = kernel.daily_briefing.generate_daily_report()
    assert report["status"] == "completed"
    assert len(report["priorities"]) >= 1
    assert "recommended_mission" in report
    assert "GOOD MORNING" in report["output"]


def test_safety_and_kernel_execution_routing():
    """Verify kernel objective handlers for Phase 76 adaptive planning components."""
    kernel = PersonalOSKernel()

    decomp = kernel.execute_objective("decompose goal", goal="Learn Machine Learning")
    assert decomp["status"] == "completed"

    replan = kernel.execute_objective("replan", goal_id="goal_01", target_hours=3.0, actual_hours=0.5)
    assert replan["status"] == "REPLANNED"

    briefing = kernel.execute_objective("briefing")
    assert briefing["status"] == "completed"
