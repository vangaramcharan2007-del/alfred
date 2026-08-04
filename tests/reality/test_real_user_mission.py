import pytest
from jarvisx.missions.unknown_mission import UnknownMissionEngine

def test_real_user_mission_execution():
    engine = UnknownMissionEngine(var_dir="var/test_user_mission")
    report = engine.execute_mission("Create a personal study tracker")
    
    assert report.success is True
    assert report.objective == "Create a personal study tracker"
    assert "YES" in report.format_cli_output()
    assert "SUCCESS" in report.format_cli_output()
