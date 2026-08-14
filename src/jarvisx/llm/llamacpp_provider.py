"""Standalone llama.cpp & GGUF Provider for Jarvis X: GENESIS.

Interfaces directly with local llama.cpp / llama-server binaries,
supporting GGUF quantized models (Q4_K_M, Q8_0), streaming, and context scaling.
"""

from __future__ import annotations
import os
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, AsyncGenerator

from jarvisx.llm.llm_provider import LLMProvider


class LlamaCppProvider(LLMProvider):
    """Direct provider interface for standalone llama.cpp HTTP server."""

    def __init__(self, endpoint: str = "http://localhost:8080", config: Optional[Dict[str, Any]] = None):
        super().__init__("llamacpp.local", config)
        self.endpoint = os.environ.get("LLAMACPP_ENDPOINT", endpoint)
        self.default_model = "gguf-local"
        self.context_window = int(self.config.get("n_ctx", 8192))
        self.is_connected = False

    async def connect(self) -> bool:
        """Probe llama.cpp server health."""
        try:
            req = urllib.request.Request(f"{self.endpoint}/health", headers={"User-Agent": "JarvisX-LlamaCpp"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                self.is_connected = resp.status == 200
                return self.is_connected
        except Exception:
            # Check /props or root endpoint
            try:
                req = urllib.request.Request(f"{self.endpoint}/props", headers={"User-Agent": "JarvisX-LlamaCpp"})
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    self.is_connected = resp.status == 200
                    return self.is_connected
            except Exception:
                self.is_connected = False
                return False

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        connected = await self.connect()
        return {
            "provider": self.name,
            "endpoint": self.endpoint,
            "status": "HEALTHY" if connected else "OFFLINE",
            "context_window": self.context_window
        }

    async def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate response via llama.cpp /completion endpoint."""
        start_t = time.time()
        payload = {
            "prompt": prompt,
            "n_predict": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "stop": ["\nUser:", "User:", "### Human:"],
            "stream": False
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(f"{self.endpoint}/completion", data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60.0) as resp:
                if resp.status == 200:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    text = res_json.get("content", "")
                    latency = round(time.time() - start_t, 3)
                    return {
                        "status": "AVAILABLE",
                        "response": text,
                        "model": model or self.default_model,
                        "provider_id": self.name,
                        "latency": latency,
                        "tokens_generated": len(text.split())
                    }
        except Exception as e:
            return {
                "status": "NOT_AVAILABLE",
                "error": f"llama.cpp generation failed: {e}",
                "model": model or self.default_model,
                "provider_id": self.name
            }

    async def stream(self, prompt: str, model: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        res = await self.generate(prompt, model, **kwargs)
        yield res.get("response", "")

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "backend": "llama.cpp GGUF engine",
            "context_window": self.context_window
        }

    def capabilities(self) -> List[str]:
        return ["chat", "code", "completion", "gguf_quantization"]
