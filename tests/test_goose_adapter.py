import pytest
import tempfile
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.goose.goose_adapter import GooseCapabilityAdapter

@pytest.mark.asyncio
async def test_goose_adapter_registration_and_execution():
    registry = CapabilityRegistry()
    adapter = GooseCapabilityAdapter()

    await adapter.register(registry)

    descriptor = registry.get("goose.engineering")
    assert descriptor is not None
    assert "implement_feature" in descriptor.supported_actions

    with tempfile.TemporaryDirectory() as tmpdir:
        res = await registry.execute(
            "goose.engineering",
            "implement_feature",
            task_description="Build User Authentication Service",
            repo_path=tmpdir
        )
        assert res["status"] == "success"
        assert "architecture_plan" in res
        assert "repository_profile" in res
