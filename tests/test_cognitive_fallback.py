import pytest
from jarvisx.cognition.cognitive_runtime import CognitiveRuntime
from jarvisx.cognition.decision_engine import DecisionEngine

@pytest.mark.asyncio
async def test_cognitive_fallback_empty():
    runtime = CognitiveRuntime()
    # If capable_agents is empty, should return None
    result = await runtime.route_task("task", [])
    assert result is None
