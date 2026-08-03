import pytest
import tempfile
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.openhands.openhands_adapter import OpenHandsCapabilityAdapter

@pytest.mark.asyncio
async def test_openhands_adapter_registration_and_execution():
    registry = CapabilityRegistry()
    adapter = OpenHandsCapabilityAdapter()

    await adapter.register(registry)

    descriptor = registry.get("openhands.engineering")
    assert descriptor is not None
    assert "implement_feature" in descriptor.supported_actions

    with tempfile.TemporaryDirectory() as tmpdir:
        res = await registry.execute(
            "openhands.engineering",
            "implement_feature",
            task_description="Add Redis Caching Layer",
            repo_path=tmpdir
        )
        assert res["status"] == "success"
        assert "architecture_plan" in res
        assert "workspace" in res
