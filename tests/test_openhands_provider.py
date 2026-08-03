import pytest
from jarvisx.capabilities.openhands.openhands_provider import OpenHandsProvider

@pytest.mark.asyncio
async def test_openhands_provider_lifecycle():
    provider = OpenHandsProvider()
    assert await provider.connect() is True

    health = await provider.health()
    assert health["provider"] == "openhands"
    assert "status" in health

    meta = provider.metadata()
    assert meta["name"] == "OpenHands Software Engineer"

    caps = provider.capabilities()
    assert "implement_feature" in caps
    assert "fix_bug" in caps

    res = await provider.execute("implement_feature", project_name="TestApp")
    assert res["status"] in ["success", "degraded_success"]
    assert "session_id" in res

    assert await provider.disconnect() is True
