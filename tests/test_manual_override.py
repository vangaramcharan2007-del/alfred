import pytest
from jarvisx.cognition.cognitive_runtime import CognitiveRuntime

@pytest.mark.asyncio
async def test_manual_override():
    runtime = CognitiveRuntime()
    overrides = {"manual_override": True, "preferred_agent": "edith"}
    result = await runtime.route_task("Task", ["friday"], overrides=overrides)
    assert result == "edith"
