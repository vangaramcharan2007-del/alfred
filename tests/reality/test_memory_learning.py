import pytest
from jarvisx.missions.unknown_mission import UnknownMissionEngine

def test_memory_learning_loop():
    engine = UnknownMissionEngine(var_dir="var/test_memory_learning")
    
    # Mission 1
    rep1 = engine.execute_mission("Prepare Operating Systems study plan")
    assert rep1.memory_updated is True
    
    # Mission 2 (retrieves experience from Mission 1)
    rep2 = engine.execute_mission("Prepare Operating Systems study plan")
    assert rep2.success is True
    assert any("[Memory Insight]" in log for log in rep2.execution_logs)
