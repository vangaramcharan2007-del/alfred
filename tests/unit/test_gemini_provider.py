"""Unit tests for GeminiLLMProvider and Gemini 1.5 Pro integration in Jarvis X."""

import pytest
from unittest.mock import patch, MagicMock
from jarvisx.llm.gemini_provider import GeminiLLMProvider
from jarvisx.llm.llm_router import LLMRouter


@pytest.mark.asyncio
async def test_gemini_provider_missing_key():
    prov = GeminiLLMProvider(config={"api_key": ""})
    with patch.object(prov, "_load_api_key", return_value=""):
        res = await prov.generate("Hello Gemini")
        assert res["status"] == "NOT_AVAILABLE"
        assert "Missing GEMINI_API_KEY" in res["error"]


@pytest.mark.asyncio
async def test_gemini_provider_mock_success():
    prov = GeminiLLMProvider(config={"api_key": "AIzaFakeTestKey1234567890"})
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'{"candidates": [{"content": {"parts": [{"text": "Gemini 1.5 Pro active response."}]}}]}'

    with patch("urllib.request.urlopen") as mock_url:
        mock_url.return_value.__enter__.return_value = mock_resp
        res = await prov.generate("Explain algorithms", model="gemini-1.5-pro")
        assert res["status"] == "AVAILABLE"
        assert res["model"] == "gemini-1.5-pro"
        assert "Gemini 1.5 Pro active response" in res["response"]


@pytest.mark.asyncio
async def test_llm_router_routes_to_gemini():
    router = LLMRouter()
    mock_gemini = MagicMock()
    mock_gemini.name = "gemini.google"
    mock_gemini.generate = pytest.importorskip("unittest.mock").AsyncMock(return_value={
        "status": "AVAILABLE",
        "provider_id": "gemini.google",
        "model": "gemini-1.5-pro",
        "response": "Architectural analysis complete by Gemini Pro.",
        "fallback_used": False
    })
    mock_gemini.connect = pytest.importorskip("unittest.mock").AsyncMock(return_value=True)

    router.registry.register(mock_gemini)
    res = await router.route_request("Use Gemini Pro to design a distributed cache architecture")
    assert res["status"] == "success"
    assert res["provider_id"] == "gemini.google"
    assert "Architectural analysis" in res["result"]["response"]
