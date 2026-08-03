import pytest
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.meta.meta_engine import MetaCognitionEngine

@pytest.mark.asyncio
async def test_meta_cognition_engine_self_analysis():
    registry = CapabilityRegistry()
    engine = MetaCognitionEngine(registry=registry)

    await engine.register(registry)

    res = await engine.run_self_analysis()
    assert "capabilities_summary" in res
    assert "system_graph" in res
    assert "improvement_plans" in res
    assert res["confidence"] > 0.80

    eval_res = await registry.execute(
        "meta.engine",
        "evaluate_decision",
        task_description="Build iOS mobile application"
    )
    assert "capability_confidence" in eval_res
    assert "knowledge_gap_score" in eval_res
