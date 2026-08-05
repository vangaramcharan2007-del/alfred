"""Unit and verification tests for Phase 51: Persistent Background Daemon & Proactive Briefing Engine.

Verifies autonomous cycle execution, proactive Daily Executive Briefing generation,
quantified HSPW time savings (> +3.0 HSPW), and strict Layer 2 architectural compliance.
"""

import pytest
from jarvisx.kernel.daemon import AlfredDaemon
from jarvisx.architecture import get_layer_for_module


def test_daemon_lifecycle_and_proactive_cycles(monkeypatch):
    """Verify AlfredDaemon starts, stops, and executes autonomous background cycles."""
    daemon = AlfredDaemon()
    
    # Muffle git check to ensure stable test environment output
    monkeypatch.setattr(daemon.os_kernel.guardian_agent.guardian.git_watcher, "check_git_status", lambda cwd: {"status": "CLEAN", "uncommitted_count": 0})

    start_res = daemon.start(interval_seconds=30)
    assert start_res["status"] == "active"
    assert daemon.is_running is True

    # Trigger proactive background sweeps
    cycle_1 = daemon.trigger_proactive_cycle()
    assert cycle_1["cycle_number"] == 1
    assert cycle_1["guardian_status"] == "audited"
    assert cycle_1["hspw_accumulated"] > 0.0

    cycle_2 = daemon.trigger_proactive_cycle()
    assert cycle_2["cycle_number"] == 2

    stop_res = daemon.stop()
    assert stop_res["status"] == "stopped"
    assert stop_res["cycles_completed"] == 2


def test_daemon_executive_briefing_and_hspw_gains(monkeypatch):
    """Verify Daily Executive Briefing synthesis and cumulative HSPW evaluation."""
    daemon = AlfredDaemon()
    monkeypatch.setattr(daemon.os_kernel.guardian_agent.guardian.git_watcher, "check_git_status", lambda cwd: {"status": "CLEAN", "uncommitted_count": 0})

    # Schedule a test study goal in the personal OS to verify inclusion in briefing
    daemon.os_kernel.execute_objective("Schedule revision for Advanced Systems Design", course="System Design", days_until_exam=2)

    briefing = daemon.generate_daily_briefing()
    assert "ALFRED DAILY EXECUTIVE BRIEFING" in briefing["output"]
    assert "[MORNING STUDY & ACADEMIC PRIORITIES]" in briefing["output"]
    assert "[OVERNIGHT PROJECT HEALTH & REGRESSION TELEMETRY]" in briefing["output"]
    assert "[ACTIONABLE EXECUTIVE ALERTS]" in briefing["output"]
    
    # Verify HSPW gain meets acceptance threshold (+3.0 HSPW minimum)
    stat = daemon.get_daemon_status()
    assert stat["briefings_generated"] == 1
    assert stat["daemon_hspw"] >= 3.0


def test_architecture_layer_compliance_for_daemon():
    """Verify jarvisx.kernel.daemon is cleanly contained under Layer 2 (Alfred Intelligence Layer)."""
    assert get_layer_for_module("jarvisx.kernel.daemon") == "alfred"
    assert get_layer_for_module("jarvisx.kernel") == "alfred"
