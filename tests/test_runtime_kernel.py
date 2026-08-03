import pytest
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.kernel.runtime_kernel import RuntimeKernel

@pytest.mark.asyncio
async def test_runtime_kernel_boot_and_health():
    registry = CapabilityRegistry()
    kernel = RuntimeKernel(registry=registry)
    await kernel.register(registry)

    boot_res = await kernel.boot()
    assert boot_res["state"] == "RUNNING"
    assert boot_res["all_healthy"] is True

    health = kernel.health_check()
    assert health["overall"] == "HEALTHY"
    assert health["online"] == boot_res["subsystems_online"]
