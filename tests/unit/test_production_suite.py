import pytest
import asyncio
from pathlib import Path
from jarvisx.runtime.runtime import JarvisRuntime
from friday.friday_assistant import FridayAssistant
from friday.academic_war_mode import AcademicWarMode
from jarvisx.observability.time_saved_tracker import TimeSavedTracker
from jarvisx.automation.desktop_actions import organize_folder, compress_folder, disk_usage
from jarvisx.missions.mission_executor import MissionExecutor
from jarvisx.missions.mission import Mission


@pytest.fixture
def runtime():
    rt = JarvisRuntime()
    asyncio.run(rt.start(print_banner=False))
    return rt


def test_system_status(runtime):
    res = asyncio.run(runtime.cli.handle_command_async("status"))
    assert res["system_health"] == "HEALTHY"
    assert res["subsystems_online"] > 0


def test_system_doctor(runtime):
    res = asyncio.run(runtime.cli.handle_command_async("doctor"))
    assert res["status"] == "COMPLETED"
    assert "checks" in res
    assert res["checks"]["git"] == "OK"


def test_academic_war_mode(runtime):
    res = asyncio.run(runtime.cli.handle_command_async("war"))
    assert res["status"] == "SUCCESS"
    assert res["result"]["target_cgpa"] == 10.0
    assert len(res["result"]["impact_ranking"]) > 0


def test_time_saved_report(runtime):
    res = asyncio.run(runtime.cli.handle_command_async("report"))
    assert res["status"] == "SUCCESS"
    assert res["result"]["status"] == "GENERATED"
    assert Path(res["result"]["path"]).exists()


def test_friday_assistant_alerts():
    assistant = FridayAssistant()
    alerts = assistant.generate_proactive_alerts()
    readiness = assistant.get_exam_readiness()
    assert isinstance(alerts, list)
    assert isinstance(readiness, list)
    assert len(readiness) > 0


def test_academic_war_mode_engine():
    awm = AcademicWarMode()
    strat = awm.get_war_strategy()
    assert strat["status"] == "ACTIVE"
    assert strat["target_cgpa"] == 10.0
    assert "top_focus" in strat


def test_time_saved_tracker():
    tracker = TimeSavedTracker()
    summary = tracker.get_summary()
    assert "today_minutes" in summary


def test_desktop_disk_usage():
    res = disk_usage(".")
    assert res["status"] == "SUCCESS"
    assert res["files"] > 0
    assert res["size_mb"] >= 0.0


def test_desktop_compress(tmp_path):
    test_dir = tmp_path / "test_folder"
    test_dir.mkdir()
    (test_dir / "sample.txt").write_text("Hello World", encoding="utf-8")
    
    res = compress_folder(str(test_dir))
    assert res["status"] == "SUCCESS"
    assert Path(res["output"]).exists()


def test_mission_executor():
    executor = MissionExecutor()
    mission = Mission(
        title="Create test calculator",
        user_request="Build a calculator module with tests",
        intent="coding",
        capability="coding",
        provider="ollama",
        steps=[]
    )
    res = asyncio.run(executor.execute(mission))
    assert mission.status == "COMPLETED"
    assert len(res["files_changed"]) > 0
    assert res["test_result"]["status"] == "PASS"
