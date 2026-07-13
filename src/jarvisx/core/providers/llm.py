from __future__ import annotations

import asyncio
import os
from jarvisx.core.providers.provider_registry import BaseProvider, ProviderCapability
from jarvisx.clients.openai_client import OpenAIClient

class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.client = OpenAIClient()
        
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("LLM", "OpenAI", 20, False)
        
    async def check_health(self) -> bool:
        return self.client.is_configured
        
    async def benchmark(self) -> float:
        return 150.0 if self.client.is_configured else float('inf')

    def generate(self, prompt: str) -> str:
        # Stub implementation mapping to OpenAIClient's capabilities (which currently only has transcribe in scaffold, but we assume it handles LLM later)
        return f"[OpenAI] {prompt}"

class GeminiProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("LLM", "Gemini", 10, False)
        
    async def check_health(self) -> bool:
        return bool(os.environ.get("GEMINI_API_KEY"))
        
    async def benchmark(self) -> float:
        return 120.0 if os.environ.get("GEMINI_API_KEY") else float('inf')

    def generate(self, prompt: str) -> str:
        return f"[Gemini] {prompt}"

class ClaudeProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("LLM", "Claude", 30, False)
        
    async def check_health(self) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
        
    async def benchmark(self) -> float:
        return 180.0 if os.environ.get("ANTHROPIC_API_KEY") else float('inf')

    def generate(self, prompt: str) -> str:
        return f"[Claude] {prompt}"

class GroqProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("LLM", "Groq", 40, False)
        
    async def check_health(self) -> bool:
        return bool(os.environ.get("GROQ_API_KEY"))
        
    async def benchmark(self) -> float:
        return 80.0 if os.environ.get("GROQ_API_KEY") else float('inf')

    def generate(self, prompt: str) -> str:
        return f"[Groq] {prompt}"

class OpenRouterProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("LLM", "OpenRouter", 50, False)
        
    async def check_health(self) -> bool:
        return bool(os.environ.get("OPENROUTER_API_KEY"))
        
    async def benchmark(self) -> float:
        return 200.0 if os.environ.get("OPENROUTER_API_KEY") else float('inf')

    def generate(self, prompt: str) -> str:
        return f"[OpenRouter] {prompt}"

class OllamaProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("LLM", "Ollama", 60, True)
        
    async def check_health(self) -> bool:
        # In a real impl, this would ping localhost:11434
        return os.environ.get("OLLAMA_HOST") is not None
        
    async def benchmark(self) -> float:
        return 500.0 if os.environ.get("OLLAMA_HOST") else float('inf')

    def generate(self, prompt: str) -> str:
        return f"[Ollama] {prompt}"

class LlamaCppProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("LLM", "llama.cpp", 70, True)
        
    async def check_health(self) -> bool:
        return os.path.exists("models/llama.cpp")
        
    async def benchmark(self) -> float:
        return 450.0 if os.path.exists("models/llama.cpp") else float('inf')

    def generate(self, prompt: str) -> str:
        return f"[llama.cpp] {prompt}"

class LocalGGUFProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("LLM", "GGUF local model", 80, True)
        
    async def check_health(self) -> bool:
        # Always available as a final fallback stub for tests
        return True
        
    async def benchmark(self) -> float:
        return 600.0

    def generate(self, prompt: str) -> str:
        return f"[Local GGUF] {prompt}"
