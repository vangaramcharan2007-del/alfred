"""Unit and Integration Tests for Phase 77: Autonomous Mission Execution Loop.

Tests MissionExecutorEngine, ExecutionMonitor, FeedbackEngine, and ExecutionSafetyGuard.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.missions.mission import Mission
from jarvisx.execution import MissionExecutorEngine, ExecutionMonitor, FeedbackEngine, ExecutionSafetyGuard


def test_mission_lifecycle_state_transitions():
    """Verify MissionExecutorEngine transitions missions across CREATED -> READY -> RUNNING -> COMPLETED."""
    kernel = PersonalOSKernel()
    executor = kernel.mission_executor

    m = Mission(title="Organize Downloads Folder", user_request="organize downloads")
    assert m.status == "PENDING" or m.status == "CREATED"

    res = executor.execute_mission(mission=m, os_kernel=kernel)
    assert res["status"] == "COMPLETED"
    assert m.status == "COMPLETED"
    assert m.result is not None


def test_execution_monitor_telemetry():
    """Verify ExecutionMonitor tracks execution time, status, memory usage, and quality score."""
    monitor = ExecutionMonitor()
    rec = monitor.record_execution_telemetry(
        mission_id="m_01",
        title="Clean System Storage",
        status="COMPLETED",
        duration_seconds=0.25,
        quality_score=1.0,
    )

    assert rec["mission_id"] == "m_01"
    assert rec["ram_usage_mb"] > 0.0
    assert rec["duration_seconds"] == 0.25

    summary = monitor.get_performance_summary()
    assert summary["total_executions"] == 1
    assert summary["success_rate"] == 1.0


def test_feedback_engine_learning_and_sqlite_storage():
    """Verify FeedbackEngine compares expected vs actual effort and stores learning in SQLite."""
    kernel = PersonalOSKernel()
    fb = kernel.feedback_engine

    res = fb.process_mission_feedback(
        mission_id="m_calculus_01",
        expected_effort_hours=2.0,
        actual_effort_hours=3.5,
        category="calculus_assignment",
    )

    assert res["difference_hours"] == 1.5
    assert res["adjustment_multiplier"] > 1.0
    assert "Future estimates increased" in res["learning"]

    # Verify memory persistence
    memories = fb.memory.search_memory("feedback_learning", top_k=5)
    assert len(memories) >= 1


def test_execution_safety_guard_rules():
    """Verify ExecutionSafetyGuard blocks destructive, communication, and financial actions without confirmation."""
    kernel = PersonalOSKernel()
    guard = kernel.execution_safety

    # Safe mission
    s1 = guard.evaluate_execution_safety(mission_title="organize downloads", confidence=0.90, user_confirmed=False)
    assert s1["permitted"] is True

    # Destructive mission without user confirmation
    s2 = guard.evaluate_execution_safety(mission_title="delete file from workspace", confidence=0.95, user_confirmed=False)
    assert s2["permitted"] is False
    assert s2["risk_level"] == "CRITICAL"
    assert s2["status"] == "REQUIRES_USER_CONFIRMATION"

    # Destructive mission WITH user confirmation
    s2_conf = guard.evaluate_execution_safety(mission_title="delete file from workspace", confidence=0.95, user_confirmed=True)
    assert s2_conf["permitted"] is True

    # Financial action without user confirmation
    s3 = guard.evaluate_execution_safety(mission_title="pay bill online", confidence=0.90, user_confirmed=False)
    assert s3["permitted"] is False
    assert s3["status"] == "REQUIRES_USER_CONFIRMATION"


def test_kernel_mission_execution_routing():
    """Verify kernel objective handlers for Phase 77 execution loop components."""
    kernel = PersonalOSKernel()

    m = Mission(title="System Cleaner Sweep", user_request="clean pc")
    exec_res = kernel.execute_objective("execute mission", mission=m)
    assert exec_res["status"] == "COMPLETED"

    fb_res = kernel.execute_objective("feedback", mission_id="m_02", expected_hours=1.0, actual_hours=1.0)
    assert fb_res["difference_hours"] == 0.0
