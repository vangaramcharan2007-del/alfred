import pytest
from jarvisx.benchmark.runner import BenchmarkRunner
from jarvisx.benchmark.definitions import MissionDefinition

def test_integration_error_recovery():
    runner = BenchmarkRunner(var_dir="var/test_recovery")
    m002 = MissionDefinition(
        mission_id="M002",
        title="Debug a broken Python project",
        description="Detect failure and recover",
        category="debugging",
        steps=["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]
    )
    res = runner.run_mission(m002)
    assert res.success is True
    assert res.steps_completed == 5
