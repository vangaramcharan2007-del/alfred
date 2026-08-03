import pytest
from jarvisx.brain.brain_controller import BrainController
from jarvisx.missions.mission_manager import MissionManager

@pytest.mark.asyncio
async def test_integration_agent_execution_flow():
    brain = BrainController()
    manager = MissionManager(brain=brain)

    res = await manager.create_and_execute_mission("Refactor error handling module")
    assert res["mission"]["status"] == "COMPLETED"
    assert res["result"]["test_result"]["exit_code"] == 0
    assert res["result"]["git_result"]["status"] == "COMMITTED"
