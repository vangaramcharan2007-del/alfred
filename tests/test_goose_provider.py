import pytest
from jarvisx.capabilities.goose.goose_provider import GooseProvider

@pytest.mark.asyncio
async def test_goose_provider_lifecycle():
    provider = GooseProvider()
    assert await provider.connect() is True

    health = await provider.health()
    assert health["status"] == "HEALTHY"
    assert health["provider"] == "goose"

    meta = provider.metadata()
    assert meta["name"] == "Goose"

    caps = provider.capabilities()
    assert "implement_feature" in caps
    assert "fix_bug" in caps

    res = await provider.execute("implement_feature", feature_name="JWT Auth")
    assert res["status"] == "success"
    assert "session_id" in res

    assert await provider.disconnect() is True
