"""Unit Tests for OpenRouter Cloud Provider and LLMRouter Fallback Engine."""

import asyncio
import io
import json
import os
import sys
import urllib.error
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.llm.openrouter_provider import OpenRouterLLMProvider
from jarvisx.llm.ollama_provider import OllamaLLMProvider
from jarvisx.llm.llm_router import LLMRouter
from jarvisx.llm.llm_registry import LLMRegistry
from jarvisx.llm.llm_provider import LLMProvider


class DummyResponse:
    def __init__(self, data: dict, status: int = 200):
        self._data = json.dumps(data).encode("utf-8")
        self.status = status

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_openrouter_provider_creation():
    """Verify OpenRouter provider instantiation, metadata, and capabilities."""
    provider = OpenRouterLLMProvider()
    assert provider.name == "openrouter.gateway"
    meta = provider.metadata()
    assert meta["provider_id"] == "openrouter.gateway"
    assert "chat" in provider.capabilities()
    assert "cloud" in provider.capabilities()
    assert len(provider.available_models) > 0


def test_openrouter_missing_api_key(monkeypatch):
    """Verify OpenRouter returns explicit NOT_AVAILABLE contract when API key is missing."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    provider = OpenRouterLLMProvider(config={"api_key": ""})

    res = asyncio.run(provider.generate("hello test"))
    assert res["status"] == "NOT_AVAILABLE"
    assert res["response"] == ""
    assert "OPENROUTER_API_KEY is not set or empty" in res["error"]
    assert res["tokens_generated"] == 0


def test_openrouter_secret_redaction():
    """Verify API keys and Bearer tokens are redacted from error logs and diagnostics."""
    fake_secret = "sk-or-v1-abcd1234efgh5678ijkl9012"
    provider = OpenRouterLLMProvider(config={"api_key": fake_secret})

    # Test direct key replacement
    sanitized1 = provider._sanitize(f"Failed to connect using key {fake_secret} on endpoint")
    assert fake_secret not in sanitized1
    assert "[REDACTED" in sanitized1

    # Test Bearer header redaction
    sanitized2 = provider._sanitize(f"Header: Authorization: Bearer {fake_secret}")
    assert fake_secret not in sanitized2
    assert "Bearer [REDACTED" in sanitized2


def test_openrouter_successful_generation(monkeypatch):
    """Verify OpenRouter parses real cloud response payload correctly."""
    mock_payload = {
        "id": "gen-12345",
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Cloud response from OpenRouter."
                }
            }
        ]
    }

    def mock_urlopen(req, timeout=None):
        return DummyResponse(mock_payload, status=200)

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    provider = OpenRouterLLMProvider(config={"api_key": "test-key"})
    res = asyncio.run(provider.generate("What is RAM?"))

    assert res["status"] == "AVAILABLE"
    assert res["response"] == "Cloud response from OpenRouter."
    assert res["provider_id"] == "openrouter.gateway"
    assert res["tokens_generated"] == 4


def test_router_ollama_success_no_fallback(monkeypatch):
    """Verify router uses local Ollama when available and does NOT invoke OpenRouter."""
    registry = LLMRegistry()

    class MockOllama(LLMProvider):
        def __init__(self):
            super().__init__(name="ollama.local")

        async def connect(self): return True
        async def disconnect(self): return True
        async def health(self): return {"status": "HEALTHY"}
        async def generate(self, prompt, model=None, **kwargs):
            return {
                "status": "AVAILABLE",
                "provider_id": "ollama.local",
                "model": "qwen2.5-coder:7b",
                "response": "Local Ollama generation.",
                "fallback_used": False
            }
        async def stream(self, prompt, model=None, **kwargs): yield ""
        def metadata(self): return {}
        def capabilities(self): return []

    class MockOpenRouter(LLMProvider):
        def __init__(self):
            super().__init__(name="openrouter.gateway")
            self.called = False

        async def connect(self): return True
        async def disconnect(self): return True
        async def health(self): return {"status": "HEALTHY"}
        async def generate(self, prompt, model=None, **kwargs):
            self.called = True
            return {"status": "AVAILABLE", "response": "Cloud response"}
        async def stream(self, prompt, model=None, **kwargs): yield ""
        def metadata(self): return {}
        def capabilities(self): return []

    mock_ollama = MockOllama()
    mock_openrouter = MockOpenRouter()
    registry.register(mock_ollama)
    registry.register(mock_openrouter)

    router = LLMRouter(registry=registry)
    res = asyncio.run(router.route_request("Explain CPU in one sentence"))

    assert res["status"] == "success"
    assert res["provider_id"] == "ollama.local"
    assert res["fallback_used"] is False
    assert res["result"]["response"] == "Local Ollama generation."
    assert mock_openrouter.called is False


def test_router_ollama_failure_openrouter_fallback(monkeypatch):
    """Verify router automatically fails over to OpenRouter when Ollama fails."""
    registry = LLMRegistry()

    class FailingOllama(LLMProvider):
        def __init__(self):
            super().__init__(name="ollama.local")

        async def connect(self): return True
        async def disconnect(self): return True
        async def health(self): return {"status": "DISCONNECTED"}
        async def generate(self, prompt, model=None, **kwargs):
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "ollama.local",
                "model": "qwen2.5-coder:7b",
                "response": "[Ollama Offline]",
                "fallback_used": True
            }
        async def stream(self, prompt, model=None, **kwargs): yield ""
        def metadata(self): return {}
        def capabilities(self): return []

    class WorkingOpenRouter(LLMProvider):
        def __init__(self):
            super().__init__(name="openrouter.gateway")
            self.default_model = "nvidia/nemotron-3-nano-30b-a3b:free"

        async def connect(self): return True
        async def disconnect(self): return True
        async def health(self): return {"status": "HEALTHY"}
        async def generate(self, prompt, model=None, **kwargs):
            return {
                "status": "AVAILABLE",
                "provider_id": "openrouter.gateway",
                "model": "nvidia/nemotron-3-nano-30b-a3b:free",
                "response": "Generated by OpenRouter cloud fallback.",
                "fallback_used": False
            }
        async def stream(self, prompt, model=None, **kwargs): yield ""
        def metadata(self): return {}
        def capabilities(self): return []

    registry.register(FailingOllama())
    registry.register(WorkingOpenRouter())

    router = LLMRouter(registry=registry)
    res = asyncio.run(router.route_request("Explain kernel architecture"))

    assert res["status"] == "success"
    assert res["provider_id"] == "openrouter.gateway"
    assert res["fallback_used"] is True
    assert res["result"]["response"] == "Generated by OpenRouter cloud fallback."


def test_router_both_providers_failure(monkeypatch):
    """Verify structured diagnostic failure contract when both local and cloud providers fail."""
    registry = LLMRegistry()

    class FailingOllama(LLMProvider):
        def __init__(self):
            super().__init__(name="ollama.local")

        async def connect(self): return True
        async def disconnect(self): return True
        async def health(self): return {"status": "DISCONNECTED"}
        async def generate(self, prompt, model=None, **kwargs):
            return {"status": "NOT_AVAILABLE", "response": "", "fallback_used": True}
        async def stream(self, prompt, model=None, **kwargs): yield ""
        def metadata(self): return {}
        def capabilities(self): return []

    class FailingOpenRouter(LLMProvider):
        def __init__(self):
            super().__init__(name="openrouter.gateway")
            self.default_model = "nvidia/nemotron-3-nano-30b-a3b:free"

        async def connect(self): return True
        async def disconnect(self): return True
        async def health(self): return {"status": "DEGRADED"}
        async def generate(self, prompt, model=None, **kwargs):
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "openrouter.gateway",
                "response": "",
                "error": "Connection timeout to cloud API"
            }
        async def stream(self, prompt, model=None, **kwargs): yield ""
        def metadata(self): return {}
        def capabilities(self): return []

    registry.register(FailingOllama())
    registry.register(FailingOpenRouter())

    router = LLMRouter(registry=registry)
    res = asyncio.run(router.route_request("Explain distributed systems"))

    assert res["status"] == "provider_unavailable"
    assert res["primary"] == "ollama.local"
    assert res["fallback"] == "openrouter.gateway"
    assert "Both local Ollama and cloud OpenRouter failed" in res["error"]
