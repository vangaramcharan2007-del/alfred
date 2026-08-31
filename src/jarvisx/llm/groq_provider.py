"""
Ultra-Fast Groq LPU Cloud LLM Provider for Jarvis X & Alfred OS.
Provides sub-second (~300ms) inference using Groq LPU acceleration with models like qwen/qwen3.8-27b, groq/compound-mini, and openai/gpt-oss-120b.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from jarvisx.llm.llm_provider import LLMProvider

logger = logging.getLogger("jarvisx.llm.groq")


class GroqLLMProvider(LLMProvider):
    """Ultra-fast Groq LPU Provider (~300ms latency)."""

    DEFAULT_MODEL = "qwen/qwen3.8-27b"
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="groq.cloud", config=config)
        self.api_key = self.config.get("api_key") or self._load_api_key()
        self.default_model = self.config.get("default_model", self.DEFAULT_MODEL)
        self.available_models = [
            "qwen/qwen3.8-27b",
            "groq/compound-mini",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.6-27b",
        ]
        self._init_client()

    def _init_client(self):
        """Initializes the client status."""
        if self.api_key:
            self.is_connected = True
        else:
            self.is_connected = False

    def _load_api_key(self) -> str:
        """Discover Groq API key from .env file, environment, or TrustEngine."""
        key = ""
        env_paths = [Path(".env"), Path("E:/project-jarvis-x/.env"), Path("friday-tony-stark-demo/.env")]
        for ep in env_paths:
            if ep.exists():
                try:
                    for line in open(ep, encoding="utf-8"):
                        line = line.strip()
                        if line.startswith("GROQ_API_KEY="):
                            k = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if k:
                                key = k
                                break
                except Exception:
                    pass
            if key:
                break

        if not key:
            key = os.environ.get("GROQ_API_KEY") or ""

        if not key:
            try:
                from jarvisx.security.trust_engine import TrustEngine
                te = TrustEngine()
                key = te.vault.get_secret("GROQ_API_KEY") or ""
            except Exception:
                pass

        return key.strip().strip('"').strip("'")

    def _sanitize(self, message: str) -> str:
        """Redact API key from error or log messages."""
        if not message:
            return ""
        sanitized = re.sub(r'gsk_[0-9A-Za-z-_]{30,}', '[REDACTED_GROQ_KEY]', message)
        if self.api_key:
            sanitized = sanitized.replace(self.api_key, "[REDACTED_GROQ_KEY]")
        return sanitized

    async def connect(self) -> bool:
        if not self.api_key:
            self.api_key = self._load_api_key()
        self._init_client()
        return bool(self.api_key)

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        has_key = bool(self.api_key)
        return {
            "status": "HEALTHY" if has_key else "DEGRADED",
            "provider_id": "groq.cloud",
            "name": "Groq LPU Cloud",
            "has_key": has_key,
            "default_model": self.default_model,
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_id": "groq.cloud",
            "name": "Groq LPU Cloud",
            "default_model": self.default_model,
            "available_models": self.available_models,
            "has_key": bool(self.api_key),
            "connected": self.is_connected,
        }

    def capabilities(self) -> List[str]:
        return ["chat", "fast_inference", "tool_use", "code_generation", "streaming"]

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream output from Groq."""
        target_model = model or self.default_model
        messages = [{"role": "user", "content": prompt}]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": target_model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            async with client.stream("POST", self.BASE_URL, headers=headers, json=payload) as resp:
                if resp.status_code == 200:
                    async for line in resp.aiter_lines():
                        if line.startswith("data: ") and line != "data: [DONE]":
                            import json
                            try:
                                chunk = json.loads(line[6:])
                                delta = chunk["choices"][0]["delta"].get("content", "")
                                if delta:
                                    yield delta
                            except Exception:
                                continue

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate response via Groq LPU REST API in ~300ms."""
        start_t = time.time()

        if not self.api_key:
            self.api_key = self._load_api_key()

        if not self.api_key:
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "groq.cloud",
                "model": model or self.default_model,
                "response": "Groq API key not found. Set GROQ_API_KEY in .env.",
                "error": "Missing GROQ_API_KEY",
                "fallback_used": True,
            }

        target_model = model or self.default_model

        system_instruction = kwargs.get("system_instruction")
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": target_model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7),
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(self.BASE_URL, headers=headers, json=payload)
                elapsed_ms = (time.time() - start_t) * 1000

                if resp.status_code == 200:
                    data = resp.json()
                    raw_text = data["choices"][0]["message"]["content"].strip()
                    tokens = data.get("usage", {}).get("total_tokens", len(raw_text.split()))

                    return {
                        "status": "HEALTHY",
                        "provider_id": "groq.cloud",
                        "model": target_model,
                        "response": raw_text,
                        "latency_ms": round(elapsed_ms, 2),
                        "tokens_used": tokens,
                        "cost": 0.0,
                        "fallback_used": False,
                    }
                else:
                    err_msg = resp.text
                    logger.warning(f"Groq API returned HTTP {resp.status_code}: {err_msg}")
                    return {
                        "status": "NOT_AVAILABLE",
                        "provider_id": "groq.cloud",
                        "model": target_model,
                        "response": "",
                        "error": self._sanitize(err_msg),
                        "latency_ms": round(elapsed_ms, 2),
                        "fallback_used": True,
                    }

        except Exception as e:
            dur = round(time.time() - start_t, 3)
            logger.error(f"Groq generation error: {e}")
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "groq.cloud",
                "model": target_model,
                "response": "",
                "error": self._sanitize(str(e)),
                "latency_ms": round(dur * 1000, 1),
                "fallback_used": True,
            }
