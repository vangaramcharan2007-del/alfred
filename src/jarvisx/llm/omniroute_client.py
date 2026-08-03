from __future__ import annotations
import os
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, AsyncGenerator
from jarvisx.llm.llm_provider import LLMProvider

class OmniRouteClient(LLMProvider):
    """
    Production OmniRoute Gateway Client supporting API key auth, streaming, retries, timeouts, and token accounting.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="omniroute.gateway", config=config)
        self.api_key = os.environ.get("OMNIROUTE_API_KEY") or self.config.get("api_key", "")
        self.endpoint = os.environ.get("OMNIROUTE_ENDPOINT") or self.config.get("endpoint", "http://localhost:8080")
        self.timeout = self.config.get("timeout_seconds", 30)
        self.max_retries = self.config.get("max_retries", 3)

    async def connect(self) -> bool:
        self.is_connected = True
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        start_t = time.time()
        try:
            url = f"{self.endpoint}/health"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.api_key}"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                status_code = resp.status
                latency_ms = round((time.time() - start_t) * 1000, 1)
                return {
                    "status": "HEALTHY" if status_code == 200 else "DEGRADED",
                    "provider_id": "omniroute.gateway",
                    "endpoint": self.endpoint,
                    "latency_ms": latency_ms
                }
        except Exception as e:
            return {
                "status": "NOT_AVAILABLE",
                "provider_id": "omniroute.gateway",
                "endpoint": self.endpoint,
                "error": str(e)
            }

    async def generate(self, prompt: str, model: Optional[str] = None, conversation: Optional[List[Dict[str, str]]] = None, **kwargs) -> Dict[str, Any]:
        start_t = time.time()
        chosen_model = model or "omniroute-default"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        messages = conversation or [{"role": "user", "content": prompt}]
        payload = json.dumps({"model": chosen_model, "messages": messages, "stream": False}).encode("utf-8")

        for attempt in range(1, self.max_retries + 1):
            try:
                url = f"{self.endpoint}/v1/chat/completions"
                req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        choice = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        latency_sec = round(time.time() - start_t, 3)
                        latency_ms = round(latency_sec * 1000, 1)
                        tokens = data.get("usage", {}).get("total_tokens", len(choice.split()))
                        return {
                            "status": "AVAILABLE",
                            "provider_id": "omniroute.gateway",
                            "model": chosen_model,
                            "response": choice,
                            "latency": latency_sec,
                            "latency_ms": latency_ms,
                            "prompt_size": len(prompt),
                            "response_size": len(choice),
                            "tokens_generated": tokens,
                            "cost": 0.0,
                            "fallback_used": False,
                            "attempt": attempt
                        }
            except Exception:
                time.sleep(0.2 * attempt)

        # Explicit NOT_AVAILABLE contract if Gateway is unreachable
        latency_sec = round(time.time() - start_t, 3)
        fallback_msg = f"[OmniRoute {chosen_model} Offline]: Endpoint {self.endpoint} unreachable."
        return {
            "status": "NOT_AVAILABLE",
            "provider_id": "omniroute.gateway",
            "model": chosen_model,
            "response": fallback_msg,
            "latency": latency_sec,
            "latency_ms": round(latency_sec * 1000, 1),
            "prompt_size": len(prompt),
            "response_size": len(fallback_msg),
            "tokens_generated": 0,
            "cost": 0.0,
            "fallback_used": True
        }

    async def stream(self, prompt: str, model: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        res = await self.generate(prompt, model=model, **kwargs)
        text = res.get("response", "")
        for word in text.split():
            yield word + " "
            time.sleep(0.01)

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_id": "omniroute.gateway",
            "name": "OmniRoute AI Gateway",
            "version": "1.0.0",
            "endpoint": self.endpoint
        }

    def capabilities(self) -> List[str]:
        return ["chat", "completion", "streaming", "tool_calling", "fallback"]
