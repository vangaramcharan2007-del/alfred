import pytest
from jarvisx.llm.ollama_provider import OllamaLLMProvider

@pytest.mark.asyncio
async def test_real_llm_provider():
    provider = OllamaLLMProvider()
    res = await provider.generate("Test prompt")
    assert res["status"] in ("AVAILABLE", "NOT_AVAILABLE")
    assert res["provider_id"] == "ollama.local"
