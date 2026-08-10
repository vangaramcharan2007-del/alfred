"""Comprehensive Unit & Integration Test Suite for Phase 105: Autonomous Operating Loop & Academic Coach."""

import os
import pytest
import shutil
import tempfile

from jarvisx.operating_loop.academic_coach import AcademicCoachEngine
from jarvisx.operating_loop.initiative_arbiter import InitiativeArbiter
from jarvisx.operating_loop.loop_engine import AutonomousOperatingLoop
from jarvisx.operating_loop.models import LearningProfile, TopicMastery
from jarvisx.operating_loop.reports import (
    format_coach_status,
    format_loop_trace,
    format_study_plan,
)
from jarvisx.reliability.backup_manager import BackupManager


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def test_academic_coach_profile_and_topic_matrix(temp_dir):
    """Verify learning profile initialization, dynamic topics, and priority calculations."""
    db_path = os.path.join(temp_dir, "test_loop.db")
    coach = AcademicCoachEngine(db_path=db_path)

    assert coach.profile.degree == "BTech"
    assert "10 CGPA" in coach.profile.primary_goal
    assert len(coach.profile.topics) >= 5

    # Check priority calculation: Graph Algorithms (low mastery + failures) should have high priority
    top_topics = coach.get_highest_priority_topics(limit=3)
    assert len(top_topics) == 3
    # Top topic priority should be greater than lower priority
    assert top_topics[0].calculate_priority_score() >= top_topics[2].calculate_priority_score()


def test_academic_coach_study_mission_synthesis(temp_dir):
    """Verify targeted study missions are generated for high-priority weak topics."""
    db_path = os.path.join(temp_dir, "test_loop.db")
    coach = AcademicCoachEngine(db_path=db_path)

    missions = coach.generate_daily_study_missions(max_missions=2)
    assert len(missions) == 2
    assert missions[0].estimated_minutes > 0
    assert len(missions[0].tasks) >= 2
    assert "Focus Sprint" in missions[0].title

    recent = coach.get_recent_missions(limit=5)
    assert len(recent) == 2
    assert recent[0].mission_id == missions[1].mission_id or recent[0].mission_id == missions[0].mission_id


def test_topic_mastery_updates_and_clamping(temp_dir):
    """Verify topic mastery updates, score clamping (0.0 - 1.0), and failure tracking."""
    db_path = os.path.join(temp_dir, "test_loop.db")
    coach = AcademicCoachEngine(db_path=db_path)

    # Boost Arrays & Strings
    updated = coach.update_topic_mastery("Arrays & Strings", mastery_delta=0.20)
    assert updated.mastery_level <= 1.0

    # Penalize with mistake
    updated_weak = coach.update_topic_mastery("Dynamic Programming", mastery_delta=-0.15, past_failure_delta=1)
    assert updated_weak.mastery_level >= 0.0
    assert updated_weak.past_failures_count >= 1


def test_initiative_arbiter_confidence_and_cooldown():
    """Verify mathematical initiative formula and cooldown throttling."""
    arbiter = InitiativeArbiter(confidence_threshold=0.75, cooldown_seconds=60.0)

    # 1. High confidence trigger (Exam in 2 days, high impact)
    res_high = arbiter.evaluate_initiative(
        goal_impact=0.95,
        urgency=0.90,
        confidence=0.85,
        user_availability=0.80,
    )
    # Score: 0.95*0.35 + 0.90*0.25 + 0.85*0.20 + 0.80*0.20 = 0.3325 + 0.225 + 0.17 + 0.16 = 0.8875
    assert res_high.score >= 0.75
    assert res_high.decision == "PROACT_NOTIFY"

    # 2. Immediate second trigger without override -> should be throttled by cooldown
    res_throttled = arbiter.evaluate_initiative(
        goal_impact=0.95,
        urgency=0.90,
        confidence=0.85,
        user_availability=0.80,
        override_cooldown=False,
    )
    assert res_throttled.decision == "SILENT_STORE"
    assert "throttled by cooldown" in res_throttled.explanation

    # 3. Low urgency / low confidence trigger -> SILENT_STORE
    res_low = arbiter.evaluate_initiative(
        goal_impact=0.20,
        urgency=0.10,
        confidence=0.30,
        user_availability=0.50,
        override_cooldown=True,
    )
    assert res_low.score < 0.75
    assert res_low.decision == "SILENT_STORE"


def test_operating_loop_8_stages_full_execution(temp_dir):
    """Verify all 8 stages of the Autonomous Operating Loop produce a valid telemetry trace."""
    db_path = os.path.join(temp_dir, "test_loop.db")
    coach = AcademicCoachEngine(db_path=db_path)
    arbiter = InitiativeArbiter(confidence_threshold=0.70)
    loop = AutonomousOperatingLoop(coach=coach, arbiter=arbiter, db_path=db_path)

    cycle = loop.run_cycle(trigger_event="SYSTEM_BOOT", override_cooldown=True)

    assert cycle.status == "SUCCESS"
    assert cycle.cycle_id.startswith("cyc_")
    assert cycle.total_latency_ms >= 0.0

    # Verify each stage in the trace
    assert "trigger_event" in cycle.observe
    assert "degree" in cycle.understand
    assert "initiative_score" in cycle.decide
    assert "generated_missions_count" in cycle.plan
    assert "prepared_study_workspaces" in cycle.execute
    assert cycle.evaluate["plan_coherence_score"] >= 0.80
    assert cycle.remember["episodic_trace_logged"] is True
    assert "playbook_update" in cycle.improve

    # Verify persistence
    recent = loop.get_recent_cycles(limit=5)
    assert len(recent) == 1
    assert recent[0].cycle_id == cycle.cycle_id


def test_format_reports_and_ascii_rendering(temp_dir):
    """Verify ASCII table formatters for coach status, study plan, and telemetry trace."""
    db_path = os.path.join(temp_dir, "test_loop.db")
    coach = AcademicCoachEngine(db_path=db_path)
    loop = AutonomousOperatingLoop(coach=coach, db_path=db_path)

    cycle = loop.run_cycle(override_cooldown=True)
    missions = coach.generate_daily_study_missions(max_missions=2)

    status_str = format_coach_status(coach.profile)
    plan_str = format_study_plan(missions)
    trace_str = format_loop_trace(cycle)

    assert "JARVIS X ACADEMIC & ENGINEERING COACH" in status_str
    assert "TOPIC MASTERY & PRIORITY MATRIX" in status_str
    assert "JARVIS X STUDY MISSIONS" in plan_str
    assert "OPERATING LOOP CYCLE TELEMETRY TRACE" in trace_str


def test_backup_manager_includes_operating_loop_db(temp_dir):
    """Verify BackupManager snapshot manifest includes operating_loop.db."""
    backup_root = os.path.join(temp_dir, "backups")
    bm = BackupManager(backup_root=backup_root)
    assert "var/db/operating_loop.db" in bm.databases_to_backup
