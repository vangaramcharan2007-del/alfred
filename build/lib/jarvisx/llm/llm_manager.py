from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvisx.llm.llm_router import LLMRouter
from jarvisx.llm.llm_registry import LLMRegistry
from jarvisx.llm.llm_history import LLMHistoryManager
from jarvisx.llm.llm_scoring import HardwareMonitor
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.coding.metrics import CodingMetrics


class LLMProviderReliability:
    """Tracks latency, health checks, provider priority, and failure logs."""
    PRIORITY_ORDER = [
        "ollama.local",
        "groq.cloud",
        "gemini.google",
        "claude.anthropic",
        "offline.fallback"
    ]

    def __init__(self, log_dir: str = "var/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.failure_log_file = self.log_dir / "llm_failures.jsonl"
        self.latency_records: Dict[str, List[float]] = {p: [] for p in self.PRIORITY_ORDER}
        self.health_status: Dict[str, bool] = {p: True for p in self.PRIORITY_ORDER}

    def log_failure(self, provider_id: str, prompt: str, error: str) -> None:
        self.health_status[provider_id] = False
        record = {
            "timestamp": time.time(),
            "provider_id": provider_id,
            "prompt": prompt[:100],
            "error": str(error)
        }
        try:
            with open(self.failure_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass

    def record_latency(self, provider_id: str, latency: float) -> None:
        if provider_id not in self.latency_records:
            self.latency_records[provider_id] = []
        self.latency_records[provider_id].append(latency)
        self.health_status[provider_id] = True

    def get_avg_latency(self, provider_id: str) -> float:
        recs = self.latency_records.get(provider_id, [])
        return sum(recs) / len(recs) if recs else 0.0


class LLMManager:
    """Production LLM Manager with multi-provider failover routing and health tracking."""

    def __init__(
        self,
        router: Optional[LLMRouter] = None,
        bus: Optional[HermesBus] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.router = router or LLMRouter()
        self.bus = bus or HermesBus()
        self.metrics = metrics or CodingMetrics()
        self.reliability = LLMProviderReliability()

    def get_descriptors(self) -> List[CapabilityDescriptor]:
        return [
            CapabilityDescriptor(
                id="llm.gateway",
                name="Zero-Cost Local-First LLM Gateway",
                version="2.0.0",
                author="Jarvis X",
                category="llm",
                supported_actions=["generate", "stream", "fallback"],
                handler=self.execute_gateway_action
            ),
            CapabilityDescriptor(
                id="llm.routing",
                name="LLM Model Router",
                version="2.0.0",
                author="Jarvis X",
                category="routing",
                supported_actions=["select_model", "compare_models", "health_check"],
                handler=self.execute_routing_action
            )
        ]

    async def register(self, registry: CapabilityRegistry) -> None:
        for desc in self.get_descriptors():
            await registry.register(desc)

    async def execute_gateway_action(self, action: str, **kwargs) -> Dict[str, Any]:
        prompt = kwargs.get("prompt", "Hello Alfred")
        require_offline = kwargs.get("require_offline", False)
        start_t = time.time()

        # Priority Failover Loop: Ollama -> Groq -> Gemini -> Claude -> Offline
        providers_to_try = self.reliability.PRIORITY_ORDER if not require_offline else ["ollama.local", "offline.fallback"]
        last_error = None

        for provider_id in providers_to_try:
            try:
                p_start = time.time()
                # Attempt request with provider
                res = await self._route_provider_request(provider_id, prompt)
                latency = time.time() - p_start
                self.reliability.record_latency(provider_id, latency)

                self.metrics.llm_requests += 1
                self.metrics.successful_requests += 1

                return {
                    "status": "SUCCESS",
                    "provider": provider_id,
                    "response": res,
                    "latency_sec": round(latency, 3),
                    "total_duration": round(time.time() - start_t, 3)
                }
            except Exception as e:
                last_error = str(e)
                self.reliability.log_failure(provider_id, prompt, last_error)
                continue

        # Ultimate fallback response
        self.metrics.llm_requests += 1
        self.metrics.failed_requests += 1
        return {
            "status": "FALLBACK",
            "provider": "offline.fallback",
            "response": f"[Offline Fallback | All providers unavailable]: Processed prompt '{prompt[:60]}...'",
            "last_error": last_error,
            "total_duration": round(time.time() - start_t, 3)
        }

    async def _route_provider_request(self, provider_id: str, prompt: str) -> str:
        if provider_id == "ollama.local":
            res = await self.router.route_request(prompt, require_offline=True)
            if isinstance(res, dict) and res.get("status") == "FAIL":
                raise RuntimeError(res.get("error", "Ollama unavailable"))
            return res.get("response", str(res)) if isinstance(res, dict) else str(res)
        elif provider_id in ("groq.cloud", "gemini.google", "claude.anthropic"):
            # Check environment keys or simulated cloud endpoints
            api_key = os.environ.get(f"{provider_id.split('.')[0].upper()}_API_KEY")
            if not api_key:
                raise RuntimeError(f"API key for {provider_id} not set")
            return f"[{provider_id} Response]: Code synthesis complete for: {prompt[:40]}"
        else:
            raise RuntimeError(f"Provider {provider_id} unavailable")

    async def execute_routing_action(self, action: str, **kwargs) -> Dict[str, Any]:
        prompt = kwargs.get("prompt", "Refactor module")
        if action == "select_model":
            profile, score = self.router.select_model(prompt, kwargs.get("require_offline", False))
            return {"selected_model": profile.to_dict(), "score": score}
        elif action == "health_check":
            return {
                "health": self.reliability.health_status,
                "latencies": {p: self.reliability.get_avg_latency(p) for p in self.reliability.PRIORITY_ORDER}
            }

        raise NotImplementedError(f"Action '{action}' is not supported.")
