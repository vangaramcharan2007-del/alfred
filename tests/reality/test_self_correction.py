import pytest
from jarvisx.missions.unknown_mission import UnknownMissionEngine

def test_self_correction_loop():
    engine = UnknownMissionEngine(var_dir="var/test_self_correction")
    report = engine.execute_mission("Build expense tracker")
    
    assert report.success is True
    assert len(report.verification_results) > 0
    assert report.autonomy_score.get("overall", 0) > 0
