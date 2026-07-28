import pytest
from jarvisx.cognition.cognitive_runtime import CognitiveRuntime
from jarvisx.cognition.decision_record import DecisionRecord
import datetime

@pytest.mark.asyncio
async def test_cognitive_runtime_routing():
    runtime = CognitiveRuntime()
    target = await runtime.route_task("Do some task", ["friday", "edith"])
    assert target in ["friday", "edith"]

@pytest.mark.asyncio
async def test_cognitive_runtime_override():
    runtime = CognitiveRuntime()
    target = await runtime.route_task("Use alfred", ["friday", "edith"], overrides={"manual_override": True, "preferred_agent": "alfred"})
    assert target == "alfred"
