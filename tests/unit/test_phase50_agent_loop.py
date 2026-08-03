"""
Unit tests for Phase 50 — Jarvis X Real Personal Agent Loop capabilities.
"""
import pytest
import asyncio
from pathlib import Path

from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider
from jarvisx.runtime.daemon import JarvisDaemon
from jarvisx.cognition.daily_engineering import DailyEngineeringContext
from jarvisx.presence.vision.screen_capture import ScreenCaptureEngine
from jarvisx.presence.vision.screen_analyzer import ScreenAnalyzer
from jarvisx.trust.risk_security_gate import RiskSecurityGate
from jarvisx.automation.computer_control import ComputerController
from friday.academic_war_mode import AcademicWarMode
from jarvisx.automation.watchers import BatteryWatcher, GitWatcher, PytestWatcher, AssignmentWatcher
from jarvisx.presence.voice.voice_assistant import VoiceAssistant
from jarvisx.observability.time_saved_tracker import TimeSavedTracker


@pytest.mark.asyncio
async def test_sqlite_memory_real_persistence(tmp_path):
    db_file = tmp_path / "test_memory.db"
    provider = SQLiteMemoryProvider(db_path=str(db_file))

    # Save memory
    await provider.save("mem_decision_1", {"type": "semantic", "subject": "FastAPI", "fact": "We chose FastAPI for high performance async endpoints."})
    await provider.save("mem_bug_1", {"type": "procedural", "subject": "Auth", "fact": "Fixed authentication token expiration by refreshing header."})

    # Search memory
    results = await provider.search("FastAPI")
    assert len(results) > 0
    assert "FastAPI" in results[0]["data"]["fact"]

    # Retrieve bug memory
    bug_results = await provider.search("token expiration")
    assert len(bug_results) > 0
    assert "Auth" in bug_results[0]["data"]["subject"]


def test_daemon_lifecycle(tmp_path):
    daemon = JarvisDaemon(var_dir=str(tmp_path))
    assert not daemon.is_running()

    start_res = daemon.start()
    assert start_res["status"] == "STARTED"
    assert daemon.is_running()

    stop_res = daemon.stop()
    assert stop_res["status"] == "STOPPED"
    assert not daemon.is_running()

    startup_res = daemon.generate_startup_script()
    assert startup_res["status"] == "GENERATED"
    assert Path(startup_res["bat_script"]).exists()


def test_daily_engineering_context():
    dec = DailyEngineeringContext()
    briefing = dec.generate_briefing()
    assert briefing["status"] == "SUCCESS"
    assert "Ramcharan" in briefing["greeting"]
    assert "briefing_text" in briefing


def test_screen_capture_and_analyzer():
    capture = ScreenCaptureEngine()
    snapshot = capture.capture_active_window(output_path="var/test_screen.png")
    assert snapshot["status"] in ("CAPTURED", "PARTIAL")

    analyzer = ScreenAnalyzer(capture_engine=capture)
    analysis = analyzer.analyze_screen()
    assert analysis["status"] == "ANALYZED"
    assert "vision_summary" in analysis


def test_risk_security_gate():
    gate = RiskSecurityGate()

    low_risk = gate.evaluate_risk("screen.capture")
    assert low_risk["risk_level"] == "LOW"

    high_risk = gate.evaluate_risk("process.kill")
    assert high_risk["risk_level"] == "HIGH"

    perm = gate.check_permission("process.kill", confirmed=False)
    assert not perm["allowed"]
    assert perm["status"] == "CONFIRMATION_REQUIRED"

    perm_confirmed = gate.check_permission("process.kill", confirmed=True)
    assert perm_confirmed["allowed"]


def test_computer_controller():
    controller = ComputerController()

    res = controller.execute_action("screen.capture", {"output": "var/test_cc.png"})
    assert res["status"] in ("SUCCESS", "PARTIAL")

    # High risk without confirmation
    high_res = controller.execute_action("process.kill", {"name": "nonexistent.exe"}, confirmed=False)
    assert high_res["status"] == "CONFIRMATION_REQUIRED"


def test_academic_war_mode():
    war = AcademicWarMode()
    strat = war.get_war_strategy()
    assert strat["status"] == "ACTIVE"
    assert strat["target_cgpa"] == 10.0
    assert "daily_recommendation" in strat


def test_watchers():
    battery = BatteryWatcher().check_battery()
    assert "status" in battery

    git_st = GitWatcher().check_git_status()
    assert git_st["status"] in ("CLEAN", "DIRTY")


def test_time_saved_tracker(tmp_path):
    db_file = tmp_path / "test_time.db"
    tracker = TimeSavedTracker(db_path=str(db_file))

    log_res = tracker.log_event("Automated test run", "engineering", 5.0, clicks_avoided=3)
    assert log_res["status"] == "SUCCESS"

    summary = tracker.get_summary()
    assert summary["today_minutes"] >= 5.0

    report_res = tracker.generate_report_file(report_path=str(tmp_path / "TIME_SAVED_REPORT.md"))
    assert report_res["status"] == "GENERATED"
    assert Path(report_res["path"]).exists()
