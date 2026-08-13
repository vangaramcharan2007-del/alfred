"""Native Google Gemini Pro & Flash LLM Provider for Jarvis X."""
from __future__ import annotations
import os
import re
import json
import time
import urllib.error
import urllib.request
from typing import Dict, Any, List, Optional
from jarvisx.llm.llm_provider import LLMProvider


class GeminiLLMProvider(LLMProvider):
    """Direct Google Gemini REST API Gateway Provider (Gemini 1.5 Pro, 2.0 Flash)."""

    DEFAULT_MODEL = "gemini-1.5-pro"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="gemini.google", config=config)
        self.api_key = self.config.get("api_key") or self._load_api_key()
        self.default_model = self.config.get("default_model", self.DEFAULT_MODEL)
        self.available_models = [
            "gemini-1.5-pro",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-2.0-flash-thinking-exp-01-21"
        ]

    def _load_api_key(self) -> str:
        """Discover Gemini API key from environment, .env file, or TrustEngine vault."""
        key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GOOGLE_GENAI_API_KEY")
            or ""
        )
        if not key and os.path.exists(".env"):
            try:
                for line in open(".env", encoding="utf-8"):
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if key:
                            break
            except Exception:
                pass
        return key

    def _sanitize(self, message: str) -> str:
        """Redact API key from error or log messages."""
        if not message:
            return ""
        sanitized = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_GEMINI_KEY]', message)
        if self.api_key:
            sanitized = sanitized.replace(self.api_key, "[REDACTED_GEMINI_KEY]")
        return sanitized

    async def connect(self) -> bool:
        """Refresh API key from environment/config and mark provider connected."""
        if not self.api_key:
            self.api_key = self._load_api_key()
        self.is_connected = bool(self.api_key)
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        has_key = bool(self.api_key or self._load_api_key())
        return {
            "status": "HEALTHY" if has_key else "DEGRADED",
            "provider_id": "gemini.google",
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
        """Generate response via Google Gemini REST API."""
        start_t = time.time()
        chosen_model = model or self.default_model

        if not self.api_key:
            self.api_key = self._load_api_key()

        if not self.api_key:
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "gemini.google",
                "model": chosen_model,
                "response": "Gemini API key not configured. Set GEMINI_API_KEY in environment or .env file.",
                "error": "Missing GEMINI_API_KEY",
                "fallback_used": True
            }

        # Format prompt / conversation for Gemini
        contents = []
        if conversation:
            for turn in conversation[-10:]:
                role = "user" if turn.get("role") in ("user", "human") else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": turn.get("content", "")}]
                })

        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 4096),
            }
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{chosen_model}:generateContent?key={self.api_key}"
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        timeout = kwargs.get("timeout", self.config.get("timeout_seconds", 30.0))

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status_code = resp.status
                body = resp.read().decode("utf-8")

                if status_code == 200:
                    data = json.loads(body)
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text = "".join(p.get("text", "") for p in parts)
                    else:
                        text = ""

                    latency_sec = round(time.time() - start_t, 3)
                    latency_ms = round(latency_sec * 1000, 1)

                    return {
                        "status": "AVAILABLE",
                        "provider_id": "gemini.google",
                        "model": chosen_model,
                        "response": text,
                        "latency": latency_sec,
                        "latency_ms": latency_ms,
                        "prompt_size": len(prompt),
                        "response_size": len(text),
                        "cost": 0.0,
                        "fallback_used": False
                    }
                else:
                    err_msg = f"Gemini HTTP Error {status_code}: {body}"
                    return {
                        "status": "NOT_AVAILABLE",
                        "provider_id": "gemini.google",
                        "model": chosen_model,
                        "response": "",
                        "error": self._sanitize(err_msg),
                        "fallback_used": True
                    }

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
            err_msg = f"Gemini HTTP Error {e.code}: {body}"
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "gemini.google",
                "model": chosen_model,
                "response": "",
                "error": self._sanitize(err_msg),
                "fallback_used": True
            }
        except Exception as ex:
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "gemini.google",
                "model": chosen_model,
                "response": "",
                "error": self._sanitize(str(ex)),
                "fallback_used": True
            }

    async def stream(self, prompt: str, model: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        """Stream tokens for Gemini generation."""
        chosen_model = model or self.default_model
        gen_res = await self.generate(prompt, model=chosen_model, **kwargs)
        full_text = gen_res.get("response", "")
        for word in full_text.split(" "):
            yield word + " "

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_id": "gemini.google",
            "name": "Google Gemini Gateway",
            "version": "1.5.0",
            "type": "cloud_gateway",
            "available_models": self.available_models
        }

    def capabilities(self) -> List[str]:
        return ["chat", "coding", "streaming", "reasoning", "vision", "long_context_2m", "cloud"]
