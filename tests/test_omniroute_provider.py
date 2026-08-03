import pytest
from jarvisx.llm.omniroute_provider import OmniRouteLLMProvider

@pytest.mark.asyncio
async def test_omniroute_provider_functionality():
    provider = OmniRouteLLMProvider()
    await provider.connect()

    health = await provider.health()
    assert health["provider_id"] == "omniroute.gateway"
    assert len(health["available_models"]) >= 2

    gen = await provider.generate("Explain quantum computing concepts", model="omniroute/gemini-1.5-pro")
    assert gen["provider_id"] == "omniroute.gateway"
    assert gen["model"] == "omniroute/gemini-1.5-pro"
