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
    assert health["online"] == 17

    status = kernel.status()
    assert status["health"]["overall"] == "HEALTHY"

@pytest.mark.asyncio
async def test_runtime_kernel_subsystem_recovery():
    kernel = RuntimeKernel()
    await kernel.boot()

    # Fail a subsystem
    kernel.subsystem_mgr.set_status("voice_runtime", "FAILED", error="Simulated audio device error")
    health_before = kernel.health_check()
    assert "voice_runtime" in health_before["degraded_subsystems"]

    # Recover failed components
    rec_res = kernel.recover_components()
    assert rec_res["recovered_count"] == 1
    assert "voice_runtime" in rec_res["recovered_subsystems"]

    health_after = kernel.health_check()
    assert health_after["overall"] == "HEALTHY"

@pytest.mark.asyncio
async def test_runtime_kernel_shutdown():
    kernel = RuntimeKernel()
    await kernel.boot()
    sd = await kernel.shutdown()
    assert sd["state"] == "STOPPED"
