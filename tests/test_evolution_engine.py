import pytest
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.meta.meta_engine import MetaCognitionEngine
from jarvisx.evolution.evolution_engine import AutonomousEvolutionEngine

@pytest.mark.asyncio
async def test_autonomous_evolution_engine_cycle():
    registry = CapabilityRegistry()
    meta_engine = MetaCognitionEngine(registry=registry)
    await meta_engine.register(registry)

    evolution_engine = AutonomousEvolutionEngine(meta_engine=meta_engine, registry=registry)
    await evolution_engine.register(registry)

    res = await evolution_engine.run_evolution_cycle()

    assert "proposal" in res
    assert "simulation" in res
    assert "mission" in res
    assert "execution" in res
    assert res["execution"]["status"] == "completed"

    eval_res = await registry.execute("evolution.engine", "detect")
    assert "proposals" in eval_res
