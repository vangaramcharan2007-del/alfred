import pytest
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.missions.mission_manager import MissionManager

@pytest.mark.asyncio
async def test_mission_manager_create_and_execute():
    registry = CapabilityRegistry()
    manager = MissionManager(registry=registry)
    await manager.register(registry)

    res = await manager.create_and_execute_mission("Create a productivity app")
    mission = res["mission"]
    result = res["result"]

    assert mission["status"] == "COMPLETED"
    assert mission["intent"] == "engineering"
    assert result["test_result"]["exit_code"] == 0
    assert result["github_pr"]["status"] in ("created", "CREATED", "NOT_AVAILABLE")
    assert "evolution_memory" in result
    assert result["evolution_memory"]["success"] is True

    history = await manager.execute_mission_action("get_history")
    assert len(history["history"]) == 1
