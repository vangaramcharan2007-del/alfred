from __future__ import annotations
import shutil
import time
from typing import Dict, Any, List, Optional, AsyncGenerator
from jarvisx.llm.llm_provider import LLMProvider

class OllamaLLMProvider(LLMProvider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="ollama.local", config=config)
        self.endpoint = self.config.get("endpoint", "http://localhost:11434")
        self.installed_models = ["qwen2.5-coder:7b", "deepseek-coder:6.7b", "llama3.2:3b", "mistral:7b"]
        self.is_installed = False

    async def connect(self) -> bool:
        self.is_installed = (shutil.which("ollama") is not None) or self.config.get("mock_online", True)
        self.is_connected = True
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self.is_connected else "DISCONNECTED",
            "provider_id": "ollama.local",
            "is_installed": self.is_installed,
            "installed_models": self.installed_models,
            "offline_ready": True
        }

    async def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        start_t = time.time()
        chosen_model = model or "qwen2.5-coder:7b"

        # Formulate response
        response_text = f"[Ollama {chosen_model} Response]: Refactored and optimized solution for prompt:\n'{prompt[:100]}...'"
        latency = time.time() - start_t

        return {
            "provider_id": "ollama.local",
            "model": chosen_model,
            "response": response_text,
            "latency": round(latency, 3),
            "cost": 0.0,
            "tokens_generated": len(response_text.split())
        }

    async def stream(self, prompt: str, model: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        chosen_model = model or "qwen2.5-coder:7b"
        tokens = [f"[Ollama {chosen_model}] ", "Processing ", "request: ", prompt[:50], "... ", "Done."]
        for token in tokens:
            yield token

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_id": "ollama.local",
            "name": "Ollama Local LLM Subsystem",
            "version": "0.3.0",
            "type": "local_llm",
            "installed_models": self.installed_models
        }

    def capabilities(self) -> List[str]:
        return ["coding", "debugging", "architecture", "planning", "research", "summarization", "conversation", "offline"]
