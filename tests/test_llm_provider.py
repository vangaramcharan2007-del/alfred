import pytest
from jarvisx.llm.ollama_provider import OllamaLLMProvider

@pytest.mark.asyncio
async def test_llm_provider_base_interface():
    provider = OllamaLLMProvider()
    assert await provider.connect() is True

    health = await provider.health()
    assert health["status"] == "HEALTHY"
    assert health["provider_id"] == "ollama.local"

    meta = provider.metadata()
    assert meta["name"] == "Ollama Local LLM Subsystem"

    caps = provider.capabilities()
    assert "coding" in caps
    assert "offline" in caps

    gen = await provider.generate("Write a quicksort in Python")
    assert gen["provider_id"] == "ollama.local"
    assert "response" in gen

    assert await provider.disconnect() is True
