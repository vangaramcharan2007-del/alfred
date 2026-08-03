import pytest
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry

@pytest.mark.asyncio
async def test_unit_capability_registry():
    registry = CapabilityRegistry()
    caps = registry.list_capabilities()
    assert isinstance(caps, list)
