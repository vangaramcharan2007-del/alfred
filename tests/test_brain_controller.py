import pytest
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.brain.brain_controller import BrainController

@pytest.mark.asyncio
async def test_brain_controller_process_request():
    registry = CapabilityRegistry()
    brain = BrainController(registry=registry)
    await brain.register(registry)

    res = await brain.process_request("Build me a productivity web application")
    assert res["intent"]["intent"] == "engineering"
    assert res["capability"] == "coding.agent"
    assert res["provider"] == "goose"
    assert res["pipeline_status"] == "READY"

    res2 = await brain.process_request("Fix the authentication bug in the login module")
    assert res2["intent"]["intent"] == "debugging"

    ctx = await brain.execute_brain_action("get_context")
    assert ctx["history_depth"] == 2
