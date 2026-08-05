"""Unit and verification tests for Phase 49: Continuous Background Assistance & Project Guardian.

Verifies periodic health checkups, git working tree monitoring, pytest regression detection,
executive telemetry report generation, and empirical HSPW tracking.
"""

import pytest
from jarvisx.automation import ProjectGuardian
from jarvisx.agents import GuardianAgent, AgentRegistry
from jarvisx.architecture import get_layer_for_module


def test_project_guardian_health_sweep(monkeypatch):
    """Verify ProjectGuardian executes diagnostic sweeps and synthesizes telemetry reports."""
    guardian = ProjectGuardian(target_dir=".")

    # Mock clean git and passing tests to isolate verification
    monkeypatch.setattr(guardian.git_watcher, "check_git_status", lambda cwd: {"status": "CLEAN", "uncommitted_count": 0})
    monkeypatch.setattr(guardian.test_watcher, "check_tests", lambda cwd: {"status": "PASS", "exit_code": 0})

    res = guardian.run_health_sweep()
    assert res["overall_status"] == "HEALTHY"
    assert len(res["alerts"]) == 0
    assert guardian._hours_saved == 0.4

    report = guardian.get_telemetry_report()
    assert "ALFRED PROJECT GUARDIAN TELEMETRY" in report["output"]
    assert "✓ Zero regressions or background conflicts detected." in report["output"]


def test_project_guardian_detects_regressions_and_dirty_git(monkeypatch):
    """Verify ProjectGuardian surfaces actionable alerts when working tree or tests regress."""
    guardian = ProjectGuardian(target_dir=".")

    monkeypatch.setattr(guardian.git_watcher, "check_git_status", lambda cwd: {"status": "DIRTY", "uncommitted_count": 3})
    monkeypatch.setattr(guardian.test_watcher, "check_tests", lambda cwd: {"status": "FAIL", "exit_code": 1})

    res = guardian.run_health_sweep()
    assert res["overall_status"] == "REGRESSION_DETECTED"
    assert len(res["alerts"]) == 2
    assert "Git working tree dirty" in res["alerts"][0]
    assert "Test regression detected" in res["alerts"][1]

    report = guardian.get_telemetry_report()
    assert "Actionable Alerts:" in report["output"]


def test_guardian_agent_workforce_integration(monkeypatch):
    """Verify GuardianAgent integrates cleanly into workforce registry and tracks HSPW savings."""
    agent = GuardianAgent(name="project_guardian", hspw_multiplier=0.5)
    monkeypatch.setattr(agent.guardian.git_watcher, "check_git_status", lambda cwd: {"status": "CLEAN", "uncommitted_count": 0})
    monkeypatch.setattr(agent.guardian.test_watcher, "check_tests", lambda cwd: {"status": "PASS", "exit_code": 0})

    registry = AgentRegistry()
    registry.register(agent)

    found = registry.discover(capability="regression_detection")
    assert "project_guardian" in found

    # Execute two checkup tasks
    out1 = agent.execute({"action": "sweep", "target_dir": "."})
    assert out1["status"] == "completed"
    assert out1["overall_status"] == "HEALTHY"

    out2 = agent.execute({"action": "monitor", "target_dir": "."})
    assert out2["status"] == "completed"

    metrics = agent.metrics()
    assert metrics["tasks_completed"] == 2
    assert metrics["hours_saved"] == 1.0  # 2 sweeps * 0.5 hspw_multiplier = 1.0 hr saved
    assert agent.guardian._hours_saved == 0.8  # Daemon internal savings tracked cleanly


def test_architecture_layer_compliance():
    """Verify jarvisx.automation.guardian is assigned cleanly to Layer 3/4 without boundary leaks."""
    assert get_layer_for_module("jarvisx.automation.guardian") == "agents"
    assert get_layer_for_module("jarvisx.agents.guardian") == "agents"
