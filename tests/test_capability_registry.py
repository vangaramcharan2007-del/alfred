import pytest
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry

@pytest.mark.asyncio
async def test_capability_registry_lifecycle():
    registry = CapabilityRegistry()

    async def sample_handler(action: str, **kwargs):
        return f"executed {action}"

    cap = CapabilityDescriptor(
        id="test.sample",
        name="Sample Capability",
        version="1.0.0",
        category="testing",
        supported_actions=["run"],
        handler=sample_handler
    )

    await registry.register(cap)
    assert len(registry.list_capabilities()) == 1
    assert registry.get("test.sample") is not None

    res = await registry.execute("test.sample", "run")
    assert res == "executed run"

    discovered = registry.discover(category="testing")
    assert len(discovered) == 1

    health = registry.health_check("test.sample")
    assert health.status == "HEALTHY"

    unreg = await registry.unregister("test.sample")
    assert unreg is True
    assert len(registry.list_capabilities()) == 0
