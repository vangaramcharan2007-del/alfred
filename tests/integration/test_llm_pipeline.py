import pytest
from jarvisx.decision.unified_decision_engine import UnifiedDecisionEngine, DecisionContext

@pytest.mark.asyncio
async def test_integration_llm_pipeline_decision():
    engine = UnifiedDecisionEngine()
    ctx = DecisionContext(task_description="Build a high performance web server", intent="engineering")
    decision = engine.decide(ctx)

    assert "model" in decision
    assert "provider" in decision
    assert decision["risk"] in ("Low", "LOW")
