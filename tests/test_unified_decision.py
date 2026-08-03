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

    assert "Goose" in decision["capability"] or decision["capability"] == "coding.agent"
    assert decision["provider"] == "goose"
    assert "Qwen" in decision["model"]
    assert decision["risk"] == "Low"
    assert decision["confidence"] >= 0.90
    assert len(decision["reasons"]) > 0

    explanation = engine.explainer.explain(decision)
    assert "Task:" in explanation
    assert "Fix authentication bug" in explanation
    assert "Decision:" in explanation
