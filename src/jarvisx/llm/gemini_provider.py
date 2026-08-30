"""
Native Google Gemini 3.6 Pro & Flash LLM Provider for Jarvis X.
Powered by the official google-genai SDK with full support for new AQ. and AIza authentication keys.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional


from jarvisx.llm.llm_provider import LLMProvider

logger = logging.getLogger("jarvisx.llm.gemini")


class GeminiLLMProvider(LLMProvider):
    """Google Gemini Cloud Provider (Gemini 3.6 Flash / Pro with 2M context)."""

    DEFAULT_MODEL = "gemini-3.6-flash"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="gemini.google", config=config)
        self.api_key = self.config.get("api_key") or self._load_api_key()
        self.default_model = self.config.get("default_model", self.DEFAULT_MODEL)
        self.available_models = [
            "gemini-3.6-flash",
            "gemini-3.6-pro",
            "gemini-flash-latest",
            "gemini-pro-latest",
        ]
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initializes the official google-genai client."""
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                self.is_connected = True
            except Exception as e:
                logger.error(f"Failed to initialize google-genai Client: {e}")
                self._client = None
                self.is_connected = False

    def _load_api_key(self) -> str:
        """Discover Gemini API key from .env file, environment, or TrustEngine."""
        key = ""
        env_paths = [Path(".env"), Path("E:/project-jarvis-x/.env"), Path("friday-tony-stark-demo/.env")]
        for ep in env_paths:
            if ep.exists():
                try:
                    for line in open(ep, encoding="utf-8"):
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                            k = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if k:
                                key = k
                                break
                except Exception:
                    pass
            if key:
                break

        if not key:
            key = (
                os.environ.get("GEMINI_API_KEY")
                or os.environ.get("GOOGLE_API_KEY")
                or os.environ.get("GOOGLE_GENAI_API_KEY")
                or ""
            )

        if not key:
            try:
                from jarvisx.security.trust_engine import TrustEngine
                te = TrustEngine()
                key = te.vault.get_secret("GEMINI_API_KEY") or te.vault.get_secret("GOOGLE_API_KEY") or ""
            except Exception:
                pass

        return key.strip().strip('"').strip("'")


    def _sanitize(self, message: str) -> str:
        """Redact API key from error or log messages."""
        if not message:
            return ""
        sanitized = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_GEMINI_KEY]', message)
        sanitized = re.sub(r'AQ\.[0-9A-Za-z-_]{35,}', '[REDACTED_GEMINI_KEY]', sanitized)
        if self.api_key:
            sanitized = sanitized.replace(self.api_key, "[REDACTED_GEMINI_KEY]")
        return sanitized

    async def connect(self) -> bool:
        if not self.api_key:
            self.api_key = self._load_api_key()
        self._init_client()
        return bool(self._client is not None)

    async def disconnect(self) -> bool:
        self._client = None
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        has_key = bool(self.api_key)
        return {
            "status": "HEALTHY" if has_key and self._client else "DEGRADED",
            "provider_id": "gemini.google",
            "has_api_key": has_key,
            "available_models": self.available_models,
            "offline_ready": False,
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_id": "gemini.google",
            "name": "Google Gemini Cloud",
            "context_window": 2000000,
            "default_model": self.default_model,
            "cloud": True,
        }

    def capabilities(self) -> List[str]:
        return [
            "llm_inference",
            "code_gen",
            "deep_reasoning",
            "multimodal_vision",
            "massive_context_2m",
        ]

    async def stream(self, prompt: str, model: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        res = await self.generate(prompt=prompt, model=model, **kwargs)
        yield res.get("response", "")

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        conversation: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response via official Google GenAI SDK."""
        start_t = time.time()

        if not self.api_key:
            self.api_key = self._load_api_key()
            self._init_client()

        if not self._client:
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "gemini.google",
                "model": model or self.default_model,
                "response": "Gemini API client not initialized. Check GEMINI_API_KEY in .env.",
                "error": "Missing or invalid GEMINI_API_KEY",
                "fallback_used": True,
            }

        target_model = "gemini-3.6-flash"
        target_model = model or self.DEFAULT_MODEL


        try:
            loop = asyncio.get_running_loop()

            def _call_gemini_interactions():
                models_to_try = [
                    "gemini-3.7-flash",
                    "gemini-3.5-flash",
                    "gemini-flash-latest",
                    "gemini-2.5-flash",
                    "gemini-3.5-flash-lite",
                ]


                last_err = None
                for m in models_to_try:
                    try:
                        # 1. Primary: Google GenAI Interactions API
                        interaction = self._client.interactions.create(
                            model=m,
                            input=prompt,
                        )
                        if hasattr(interaction, "output_text") and interaction.output_text:
                            return interaction.output_text.strip()
                        if hasattr(interaction, "text") and interaction.text:
                            return interaction.text.strip()
                        return str(interaction)
                    except Exception as ex1:
                        # 2. Fallback: models.generate_content
                        try:
                            resp = self._client.models.generate_content(
                                model=m,
                                contents=prompt,
                            )
                            if hasattr(resp, "text") and resp.text:
                                return resp.text.strip()
                        except Exception as ex2:
                            last_err = ex2
                            continue

                if last_err:
                    raise last_err
                return "Gemini response empty."

            raw_text = await loop.run_in_executor(None, _call_gemini_interactions)
            elapsed_ms = (time.time() - start_t) * 1000

            return {
                "status": "HEALTHY",
                "provider_id": "gemini.google",
                "model": target_model,
                "response": raw_text,
                "latency_ms": round(elapsed_ms, 2),
                "tokens_used": len(raw_text.split()),
                "cost": 0.0,
                "fallback_used": False,
            }

        except Exception as e:
            dur = round(time.time() - start_t, 3)
            logger.error(f"Gemini generation error: {e}")
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "gemini.google",
                "model": target_model,
                "response": "",
                "error": self._sanitize(str(e)),
                "latency": dur,
                "latency_ms": round(dur * 1000, 1),
                "fallback_used": True,
            }

