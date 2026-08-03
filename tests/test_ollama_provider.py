import pytest
from jarvisx.llm.ollama_provider import OllamaLLMProvider

@pytest.mark.asyncio
async def test_ollama_provider_functionality():
    provider = OllamaLLMProvider()
    await provider.connect()

    health = await provider.health()
    assert health["offline_ready"] is True
    assert len(health["installed_models"]) >= 3

    chunks = []
    async for chunk in provider.stream("Write a binary search algorithm"):
        chunks.append(chunk)

    assert len(chunks) > 0
    assert "[Ollama" in chunks[0]
