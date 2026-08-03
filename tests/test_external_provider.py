import pytest
from jarvisx.capabilities.external.external_provider import (
    OllamaProvider, LiteLLMProvider, OpenRouterProvider, GooseProvider, OpenHandsProvider
)

@pytest.mark.asyncio
async def test_external_providers():
    providers = [
        OllamaProvider(),
        LiteLLMProvider(),
        OpenRouterProvider(),
        GooseProvider(),
        OpenHandsProvider()
    ]

    for p in providers:
        assert await p.connect() is True
        health = await p.health()
        assert health["status"] == "HEALTHY"
        meta = p.metadata()
        assert "name" in meta
        caps = p.capabilities()
        assert len(caps) >= 1

        exec_res = await p.execute("default_action", param="test")
        assert exec_res["provider"] == p.name
        assert await p.disconnect() is True
