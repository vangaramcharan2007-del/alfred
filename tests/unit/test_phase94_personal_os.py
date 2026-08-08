"""Unit Tests for Phase 94: Personal OS Layer."""

import pytest
import time
from pathlib import Path
from jarvisx.personal_os.models import Goal, GoalStatus, Milestone, TopicMastery, Evidence
from jarvisx.personal_os.life_memory import LifeMemory
from jarvisx.personal_os.goal_manager import GoalManager
from jarvisx.personal_os.syllabus_tracker import SyllabusTracker
from jarvisx.personal_os.habit_tracker import HabitTracker
from jarvisx.personal_os.priority_engine import PriorityEngine
from jarvisx.personal_os.personal_os_engine import PersonalOSEngine


def test_goal_persistence_and_risk_evaluation():
    db_file = "var/test_os/test_life.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = LifeMemory(db_file)
    gm = GoalManager(mem)
    g = gm.create_goal("Achieve 10 CGPA in Semester", category="academic", target_date="2026-11-30")
    assert g.status == GoalStatus.ACTIVE

    # Simulate restart by creating new GoalManager pointing to same DB
    new_gm = GoalManager(LifeMemory(db_file))
    reloaded = new_gm.get_goal(g.id)
    assert reloaded is not None
    assert reloaded.title == "Achieve 10 CGPA in Semester"

    # Evaluate Risk State
    risk_goal = new_gm.evaluate_goal_risk(g.id, average_topic_mastery=42.0)
    assert risk_goal.status == GoalStatus.AT_RISK
    assert "below the 50% safety threshold" in risk_goal.risk_reason


def test_syllabus_tracker_and_evidence():
    db_file = "var/test_os/test_syllabus.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = LifeMemory(db_file)
    st = SyllabusTracker(mem)
    ev = Evidence(type="failed_quiz", description="Scored 1/5 on Java polymorphism", weight=0.4, timestamp=time.time())
    st.record_revision("Java & OOP", "Unit 3", "Polymorphism", new_mastery=35.0, evidence=ev)

    weak = st.get_weak_areas(threshold=50.0)
    assert len(weak) >= 1
    assert weak[0].mastery_score == 35.0
    assert len(weak[0].evidence) == 1
    assert weak[0].evidence[0].type == "failed_quiz"


def test_habit_tracker_and_pattern_detection():
    db_file = "var/test_os/test_habits.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = LifeMemory(db_file)
    ht = HabitTracker(mem)
    ht.log_session("deep_work", 3.0, "academic", "2026-08-05")
    ht.log_session("leetcode", 2.0, "engineering", "2026-08-06")
    ht.log_session("revision", 0.5, "academic", "2026-08-07")

    summary = ht.get_habit_summary()
    assert summary["total_logs"] >= 3
    assert summary["average_daily_hours"] > 0.0
    assert len(summary["patterns_detected"]) >= 1


def test_priority_engine_explainability():
    db_file = "var/test_os/test_priority.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = LifeMemory(db_file)
    pe = PriorityEngine(memory=mem)
    prios = pe.calculate_daily_priorities()
    assert len(prios) >= 1

    top = prios[0]
    assert top.score > 50.0
    # Assert explainability elements
    assert "weakness" in top.explanation.lower()
    assert "deadline" in top.explanation.lower()
    assert "breakdown" in top.to_dict()
    assert "weakness" in top.breakdown


def test_personal_os_to_mission_runtime_handshake():
    engine = PersonalOSEngine()
    res = engine.dispatch_top_priority_mission()
    assert res["status"] == "DISPATCHED_AND_COMPLETED"
    assert "mission_goal" in res
    assert res["mission_result"]["status"] == "COMPLETED"
