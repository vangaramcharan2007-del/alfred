from __future__ import annotations
import time
from typing import Dict, Any, List, Optional, Tuple, AsyncGenerator
from jarvisx.llm.llm_profile import LLMProfile
from jarvisx.llm.llm_scoring import LLMScorer, HardwareMonitor, LLMTaskClassifier
from jarvisx.llm.llm_history import LLMHistoryManager
from jarvisx.llm.llm_registry import LLMRegistry
from jarvisx.llm.ollama_provider import OllamaLLMProvider
from jarvisx.llm.omniroute_provider import OmniRouteLLMProvider
from jarvisx.llm.openrouter_provider import OpenRouterLLMProvider

class LLMRouter:
    def __init__(
        self,
        registry: Optional[LLMRegistry] = None,
        scorer: Optional[LLMScorer] = None,
        history: Optional[LLMHistoryManager] = None
    ):
        self.registry = registry or LLMRegistry()
        self.scorer = scorer or LLMScorer()
        self.history = history or LLMHistoryManager()
        self.profiles: List[LLMProfile] = []

        self._populate_profiles()
        self._ensure_default_providers()

    def _ensure_default_providers(self):
        if not self.registry.get("ollama.local"):
            self.registry.register(OllamaLLMProvider())
        if not self.registry.get("omniroute.gateway"):
            self.registry.register(OmniRouteLLMProvider())
        if not self.registry.get("openrouter.gateway"):
            self.registry.register(OpenRouterLLMProvider())

    def _populate_profiles(self):
        self.profiles = [
            LLMProfile(
                provider_id="ollama.local",
                model_name="qwen2.5-coder:7b",
                context_window=128000,
                latency=0.2,
                cost=0.0,
                coding_score=0.97,
                reasoning_score=0.92,
                tool_support=True,
                streaming_support=True,
                vision_support=False,
                offline_support=True,
                privacy_level="HIGH",
                hardware_requirements={"ram_gb": 8, "vram_gb": 4}
            ),
            LLMProfile(
                provider_id="ollama.local",
                model_name="deepseek-coder:6.7b",
                context_window=64000,
                latency=0.25,
                cost=0.0,
                coding_score=0.96,
                reasoning_score=0.90,
                tool_support=True,
                streaming_support=True,
                vision_support=False,
                offline_support=True,
                privacy_level="HIGH",
                hardware_requirements={"ram_gb": 8, "vram_gb": 4}
            ),
            LLMProfile(
                provider_id="ollama.local",
                model_name="llama3.2:3b",
                context_window=128000,
                latency=0.1,
                cost=0.0,
                coding_score=0.88,
                reasoning_score=0.85,
                tool_support=True,
                streaming_support=True,
                vision_support=False,
                offline_support=True,
                privacy_level="HIGH",
                hardware_requirements={"ram_gb": 4, "vram_gb": 2}
            ),
            LLMProfile(
                provider_id="omniroute.gateway",
                model_name="omniroute/gemini-1.5-pro",
                context_window=1000000,
                latency=0.4,
                cost=0.001,
                coding_score=0.98,
                reasoning_score=0.98,
                tool_support=True,
                streaming_support=True,
                vision_support=True,
                offline_support=False,
                privacy_level="MEDIUM",
                hardware_requirements={"ram_gb": 1, "vram_gb": 0}
            ),
            LLMProfile(
                provider_id="omniroute.gateway",
                model_name="omniroute/claude-3-5-sonnet",
                context_window=200000,
                latency=0.35,
                cost=0.003,
                coding_score=0.99,
                reasoning_score=0.99,
                tool_support=True,
                streaming_support=True,
                vision_support=True,
                offline_support=False,
                privacy_level="MEDIUM",
                hardware_requirements={"ram_gb": 1, "vram_gb": 0}
            )
        ]

    def select_model(
        self,
        prompt: str,
        require_offline: bool = False
    ) -> Tuple[LLMProfile, float]:
        hw = HardwareMonitor.get_hardware_specs()

        best_profile: Optional[LLMProfile] = None
        best_score = -1.0

        for p in self.profiles:
            hist_success = self.history.get_success_rate(p.provider_id, p.model_name)
            score = self.scorer.compute_score(
                profile=p,
                prompt=prompt,
                hardware=hw,
                require_offline=require_offline,
                historical_success_rate=hist_success
            )

            if score > best_score:
                best_score = score
                best_profile = p

        if not best_profile:
            best_profile = self.profiles[0]
            best_score = 0.5

        return best_profile, round(best_score, 3)

    async def route_request(
        self,
        prompt: str,
        require_offline: bool = False,
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        task_cat = LLMTaskClassifier.classify_request(prompt)

        if model_override:
            profile = next((p for p in self.profiles if p.model_name == model_override), self.profiles[0])
            score = 1.0
        else:
            profile, score = self.select_model(prompt, require_offline=require_offline)

        provider = self.registry.get(profile.provider_id)
        if not provider:
            # Fallback to local default
            provider = self.registry.get("ollama.local")

        print(f"[LLM] Provider: {profile.provider_id}")
        print(f"[LLM] Model: {profile.model_name}")

        await provider.connect()
        output = await provider.generate(prompt=prompt, model=profile.model_name)

        resp_preview = output.get("response", "")[:60].replace("\n", " ")
        print(f"[LLM] Response received: \"{resp_preview}...\" ({len(output.get('response', ''))} chars)")

        self.history.record_outcome(
            provider_id=profile.provider_id,
            model_name=profile.model_name,
            task_category=task_cat,
            success=True,
            latency=output.get("latency", 0.1),
            cost=output.get("cost", 0.0)
        )

        return {
            "status": "success",
            "selected_model": profile.model_name,
            "provider_id": profile.provider_id,
            "score": score,
            "task_category": task_cat,
            "result": output
        }

    def route_request_sync(
        self,
        prompt: str,
        require_offline: bool = False,
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronously route request through the LLMRouter."""
        import asyncio
        import concurrent.futures

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(asyncio.run, self.route_request(prompt, require_offline, model_override))
                    return future.result()
            else:
                return loop.run_until_complete(self.route_request(prompt, require_offline, model_override))
        except RuntimeError:
            return asyncio.run(self.route_request(prompt, require_offline, model_override))

    async def stream_request(
        self,
        prompt: str,
        require_offline: bool = False
    ) -> AsyncGenerator[str, None]:
        profile, _ = self.select_model(prompt, require_offline=require_offline)
        provider = self.registry.get(profile.provider_id) or self.registry.get("ollama.local")
        await provider.connect()

        async for chunk in provider.stream(prompt=prompt, model=profile.model_name):
            yield chunk

    def fallback_model(
        self,
        current_model_name: str,
        prompt: str
    ) -> Tuple[LLMProfile, float]:
        for p in self.profiles:
            if p.model_name != current_model_name and p.offline_support:
                return p, 0.90
        return self.profiles[0], 0.50

    def compare_models(self, prompt: str, count: int = 3) -> List[Dict[str, Any]]:
        hw = HardwareMonitor.get_hardware_specs()
        scored = []
        for p in self.profiles:
            hist_success = self.history.get_success_rate(p.provider_id, p.model_name)
            s = self.scorer.compute_score(profile=p, prompt=prompt, hardware=hw, historical_success_rate=hist_success)
            scored.append({"profile": p.to_dict(), "score": round(s, 3)})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:count]
