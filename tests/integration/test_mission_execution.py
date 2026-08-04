import pytest
from jarvisx.benchmark.runner import BenchmarkRunner
from jarvisx.benchmark.definitions import get_all_missions

def test_integration_mission_execution():
    runner = BenchmarkRunner(var_dir="var/test_missions")
    missions = get_all_missions()
    assert len(missions) == 5

    # Run Mission 001
    res1 = runner.run_mission(missions[0])
    assert res1.success is True
    assert res1.steps_completed == 6

    # Run Mission 005
    res5 = runner.run_mission(missions[4])
    assert res5.success is True
