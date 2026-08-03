import pytest
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.llm.llm_manager import LLMManager

@pytest.mark.asyncio
async def test_llm_manager_registration_and_execution():
    registry = CapabilityRegistry()
    manager = LLMManager()

    await manager.register(registry)

    descriptor = registry.get("llm.gateway")
    assert descriptor is not None
    assert "generate" in descriptor.supported_actions

    hw_res = await registry.execute("llm.analysis", "detect_hardware")
    assert "hardware" in hw_res

    gen_res = await registry.execute(
        "llm.gateway",
        "generate",
        prompt="Write a Python script for file hashing",
        require_offline=True
    )
    assert gen_res["status"] == "success"
    assert "result" in gen_res
