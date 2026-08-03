import pytest
from jarvisx.decision.decision_context import DecisionContext
from jarvisx.decision.unified_decision_engine import UnifiedDecisionEngine
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry

@pytest.mark.asyncio
async def test_unified_decision_engine():
    registry = CapabilityRegistry()
    engine = UnifiedDecisionEngine(registry=registry)
    await engine.register(registry)

    ctx = DecisionContext(task_description="Fix authentication bug", intent="debugging")
    decision = engine.decide(ctx)

    assert decision["capability"] == "coding.agent"
    assert decision["provider"] == "goose"
    assert decision["model"] == "qwen2.5-coder:7b"
    assert decision["risk"] == "LOW"
    assert decision["confidence"] >= 0.90
