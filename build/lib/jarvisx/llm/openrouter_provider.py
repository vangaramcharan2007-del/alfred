"""OpenRouter Cloud Multi-Model Gateway Provider for Jarvis X."""
from __future__ import annotations
import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from typing import Dict, Any, List, Optional, AsyncGenerator
from jarvisx.llm.llm_provider import LLMProvider

logger = logging.getLogger("jarvisx.llm.openrouter")


class OpenRouterLLMProvider(LLMProvider):
    """OpenRouter Multi-Model Cloud Gateway Provider."""

    DEFAULT_MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="openrouter.gateway", config=config)
        self.gateway_url = self.config.get("gateway_url", "https://openrouter.ai/api/v1")
        self.api_key = self.config.get("api_key") or os.environ.get("OPENROUTER_API_KEY", "")
        self.default_model = self.config.get("default_model", self.DEFAULT_MODEL)
        self.available_models = [
            "nvidia/nemotron-3-nano-30b-a3b:free",
            "meta-llama/llama-3.1-8b-instruct",
            "google/gemma-4-26b-a4b-it:free",
            "liquid/lfm-2.5-2.6b:free",
            "google/gemini-2.0-flash-001"
        ]

    def _sanitize(self, message: str) -> str:
        """Redact API keys or sensitive authorization headers from log/error strings."""
        if not message:
            return ""
        sanitized = re.sub(r'Bearer\s+[A-Za-z0-9_\-\.]+', 'Bearer [REDACTED]', message)
        sanitized = re.sub(r'sk-[A-Za-z0-9_\-\.]+', '[REDACTED_KEY]', sanitized)
        if self.api_key:
            sanitized = sanitized.replace(self.api_key, "[REDACTED_API_KEY]")
        return sanitized

    async def connect(self) -> bool:
        """Refresh API key from environment/config and mark provider connected."""
        if not self.api_key:
            self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.is_connected = bool(self.api_key)
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        has_key = bool(self.api_key or os.environ.get("OPENROUTER_API_KEY", ""))
        return {
            "status": "HEALTHY" if has_key else "DEGRADED",
            "provider_id": "openrouter.gateway",
            "gateway_url": self.gateway_url,
            "has_api_key": has_key,
            "available_models": self.available_models,
            "offline_ready": False
        }

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        conversation: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response via OpenRouter cloud completions API."""
        start_t = time.time()
        chosen_model = model or self.default_model

        # Refresh API key in case it was set after initialization
        if not self.api_key:
            self.api_key = os.environ.get("OPENROUTER_API_KEY", "")

        if not self.api_key:
            latency_sec = round(time.time() - start_t, 3)
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "openrouter.gateway",
                "model": chosen_model,
                "response": "",
                "error": "OPENROUTER_API_KEY is not set or empty.",
                "latency": latency_sec,
                "latency_ms": round(latency_sec * 1000, 1),
                "prompt_size": len(prompt),
                "response_size": 0,
                "cost": 0.0,
                "tokens_generated": 0,
                "fallback_used": False
            }

        timeout_sec = kwargs.get("timeout", self.config.get("timeout_seconds", 30.0))
        temperature = kwargs.get("temperature", 0.2)

        messages = []
        if conversation:
            messages.extend(conversation[-10:])
        messages.append({"role": "user", "content": prompt})

        url = f"{self.gateway_url}/chat/completions"
        payload_dict = {
            "model": chosen_model,
            "messages": messages,
            "temperature": temperature
        }
        payload = json.dumps(payload_dict).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/vangaramcharan2007-del/alfred",
            "X-Title": "Alfred OS",
            "User-Agent": "JarvisX-Alfred"
        }

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        response_text = choices[0]["message"].get("content", "")
                    else:
                        response_text = ""

                    latency_sec = round(time.time() - start_t, 3)
                    latency_ms = round(latency_sec * 1000, 1)
                    actual_model = data.get("model", chosen_model)

                    return {
                        "status": "AVAILABLE",
                        "provider_id": "openrouter.gateway",
                        "model": actual_model,
                        "response": response_text,
                        "latency": latency_sec,
                        "latency_ms": latency_ms,
                        "prompt_size": len(prompt),
                        "response_size": len(response_text),
                        "cost": 0.0,
                        "tokens_generated": len(response_text.split()),
                        "fallback_used": False
                    }
                else:
                    err_msg = f"OpenRouter returned non-200 status code: {resp.status}"
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode("utf-8", errors="ignore")
                err_msg = f"OpenRouter HTTP Error {e.code}: {err_body}"
            except Exception:
                err_msg = f"OpenRouter HTTP Error {e.code}: {e.reason}"
        except Exception as e:
            err_msg = f"OpenRouter connection failed: {str(e)}"

        sanitized_error = self._sanitize(err_msg)
        logger.warning(f"[OpenRouter] API Error: {sanitized_error}")

        latency_sec = round(time.time() - start_t, 3)
        return {
            "status": "NOT_AVAILABLE",
            "provider_id": "openrouter.gateway",
            "model": chosen_model,
            "response": "",
            "error": sanitized_error,
            "latency": latency_sec,
            "latency_ms": round(latency_sec * 1000, 1),
            "prompt_size": len(prompt),
            "response_size": 0,
            "cost": 0.0,
            "tokens_generated": 0,
            "fallback_used": False
        }

    async def stream(self, prompt: str, model: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        chosen_model = model or self.default_model
        tokens = [f"[OpenRouter {chosen_model}] ", "Streaming ", "response: ", prompt[:50], "..."]
        for token in tokens:
            yield token

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_id": "openrouter.gateway",
            "name": "OpenRouter Multi-Model Gateway",
            "version": "1.0.0",
            "type": "cloud_gateway",
            "available_models": self.available_models
        }

    def capabilities(self) -> List[str]:
        return ["chat", "coding", "streaming", "reasoning", "multi_model", "cloud"]
