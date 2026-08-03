import pytest
from jarvisx.capabilities.external.external_provider import OllamaProvider, GooseProvider
from jarvisx.capabilities.external.provider_registry import ProviderRegistry

@pytest.mark.asyncio
async def test_provider_registry():
    registry = ProviderRegistry()
    ollama = OllamaProvider()
    goose = GooseProvider()

    await registry.register_provider(ollama)
    await registry.register_provider(goose)

    assert len(registry.list_providers()) == 2
    assert registry.get_provider("ollama") is not None
    assert registry.get_provider("goose") is not None

    unreg = await registry.unregister_provider("ollama")
    assert unreg is True
    assert len(registry.list_providers()) == 1
