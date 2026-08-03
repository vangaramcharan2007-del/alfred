import pytest
from jarvisx.capabilities.external.external_provider import OllamaProvider, OpenHandsProvider
from jarvisx.capabilities.external.provider_registry import ProviderRegistry
from jarvisx.capabilities.external.provider_router import ProviderRouter

@pytest.mark.asyncio
async def test_provider_router():
    registry = ProviderRegistry()
    await registry.register_provider(OllamaProvider())
    await registry.register_provider(OpenHandsProvider())

    router = ProviderRouter(registry=registry)

    assert router.is_provider_enabled("ollama") is True

    res = await router.route_execution("ollama", "generate", prompt="Hello world")
    assert res["provider"] == "ollama"

    p = router.find_provider_for_capability("code_completion")
    assert p is not None
    assert p.name == "ollama"
