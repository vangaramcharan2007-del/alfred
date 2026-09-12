"""Unit tests for GeminiLLMProvider and Gemini 1.5 Pro integration in Jarvis X."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from jarvisx.llm.gemini_provider import GeminiLLMProvider
from jarvisx.llm.llm_router import LLMRouter


@pytest.mark.asyncio
async def test_gemini_provider_missing_key():
    prov = GeminiLLMProvider(config={"api_key": ""})
    with patch.object(prov, "_load_api_key", return_value=""):
        res = await prov.generate("Hello Gemini")
        assert res["status"] == "NOT_AVAILABLE"
        # The provider's message is "Missing or invalid GEMINI_API_KEY", so the
        # old assertion on the literal substring "Missing GEMINI_API_KEY" could
        # never match -- "or invalid" sits between the two words. Assert on the
        # part that actually identifies the problem.
        assert "GEMINI_API_KEY" in res["error"]


@pytest.mark.asyncio
async def test_gemini_provider_mock_success():
    prov = GeminiLLMProvider(config={"api_key": "AIzaFakeTestKey1234567890"})

    # This test used to patch urllib.request.urlopen and feed back a raw
    # candidates/parts JSON body. The provider no longer uses urllib at all --
    # _init_client() builds a google.genai Client and generate() calls
    # client.interactions.create(), so that patch intercepted nothing and the
    # call fell straight through to NOT_AVAILABLE. Mock the SDK seam instead.
    interaction = MagicMock()
    interaction.output_text = "Gemini 1.5 Pro active response."

    with patch.object(prov._client.interactions, "create", return_value=interaction):
        res = await prov.generate("Explain algorithms", model="gemini-1.5-pro")
        # Success status for gemini and groq is "HEALTHY"; "AVAILABLE" is the
        # convention for the cloud/mesh/ollama providers. llm_router.py checks
        # for "HEALTHY" on this provider specifically.
        assert res["status"] == "HEALTHY"
        assert res["model"] == "gemini-1.5-pro"
        assert "Gemini 1.5 Pro active response" in res["response"]


@pytest.mark.asyncio
async def test_llm_router_routes_to_gemini():
    router = LLMRouter()
    mock_gemini = MagicMock()
    mock_gemini.name = "gemini.google"
    # llm_router.py gates the gemini route on `status == "HEALTHY"`, not
    # "AVAILABLE" -- that is the gemini/groq convention, while "AVAILABLE"
    # belongs to the cloud/mesh/ollama providers. The mock previously returned
    # "AVAILABLE", so the router rejected its own provider, fell through to
    # local Ollama, and the test failed with provider_unavailable (plus a real
    # connection attempt to 127.0.0.1:11434).
    mock_gemini.generate = AsyncMock(return_value={
        "status": "HEALTHY",
        "provider_id": "gemini.google",
        "model": "gemini-3.6-flash",
        "response": "Architectural analysis complete by Gemini Pro.",
        "fallback_used": False
    })
    mock_gemini.connect = AsyncMock(return_value=True)

    router.registry.register(mock_gemini)
    res = await router.route_request("Use Gemini Pro to design a distributed cache architecture")
    assert res["status"] == "success"
    assert res["provider_id"] == "gemini.google"
    assert "Architectural analysis" in res["result"]["response"]
