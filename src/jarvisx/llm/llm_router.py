from __future__ import annotations
import os
import time
from typing import Dict, Any, List, Optional, Tuple, AsyncGenerator
from jarvisx.llm.llm_profile import LLMProfile
from jarvisx.llm.llm_scoring import LLMScorer, HardwareMonitor, LLMTaskClassifier
from jarvisx.llm.llm_history import LLMHistoryManager
from jarvisx.llm.llm_registry import LLMRegistry
from jarvisx.llm.ollama_provider import OllamaLLMProvider
from jarvisx.llm.omniroute_provider import OmniRouteLLMProvider
from jarvisx.llm.openrouter_provider import OpenRouterLLMProvider
from jarvisx.llm.gemini_provider import GeminiLLMProvider
from jarvisx.llm.groq_provider import GroqLLMProvider



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
        if not self.registry.get("groq.cloud"):
            self.registry.register(GroqLLMProvider())
        if not self.registry.get("gemini.google"):
            self.registry.register(GeminiLLMProvider())
        if not self.registry.get("omniroute.gateway"):
            self.registry.register(OmniRouteLLMProvider())
        if not self.registry.get("openrouter.gateway"):
            self.registry.register(OpenRouterLLMProvider())


    def _populate_profiles(self):
        self.profiles = [
            LLMProfile(
                provider_id="ollama.local",
                model_name="qwen2.5-coder:1.5b",
                context_window=64000,
                latency=0.05,
                cost=0.0,
                coding_score=0.94,
                reasoning_score=0.88,
                tool_support=True,
                streaming_support=True,
                vision_support=False,
                offline_support=True,
                privacy_level="HIGH",
                hardware_requirements={"ram_gb": 1, "vram_gb": 1}
            ),
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
                provider_id="gemini.google",
                model_name="gemini-1.5-pro",
                context_window=2000000,
                latency=0.3,
                cost=0.0,
                coding_score=0.99,
                reasoning_score=0.99,
                tool_support=True,
                streaming_support=True,
                vision_support=True,
                offline_support=False,
                privacy_level="HIGH",
                hardware_requirements={"ram_gb": 0, "vram_gb": 0}
            ),
            LLMProfile(
                provider_id="gemini.google",
                model_name="gemini-2.0-flash",
                context_window=1000000,
                latency=0.15,
                cost=0.0,
                coding_score=0.98,
                reasoning_score=0.97,
                tool_support=True,
                streaming_support=True,
                vision_support=True,
                offline_support=False,
                privacy_level="HIGH",
                hardware_requirements={"ram_gb": 0, "vram_gb": 0}
            ),
            LLMProfile(
                provider_id="openrouter.gateway",
                model_name="nvidia/nemotron-3-nano-30b-a3b:free",
                context_window=128000,
                latency=0.5,
                cost=0.0,
                coding_score=0.95,
                reasoning_score=0.94,
                tool_support=True,
                streaming_support=True,
                vision_support=False,
                offline_support=False,
                privacy_level="MEDIUM",
                hardware_requirements={"ram_gb": 0, "vram_gb": 0}
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

        # Direct Groq LPU Cloud Route (Ultra-fast ~300ms inference)
        has_groq_key = bool(os.environ.get("GROQ_API_KEY"))
        groq_provider = self.registry.get("groq.cloud")
        if not has_groq_key and groq_provider:
            has_groq_key = bool(getattr(groq_provider, "api_key", ""))

        if has_groq_key and not require_offline:
            if groq_provider:
                groq_model = "qwen/qwen3.8-27b"
                print(f"[LLM] Primary Ultra-Fast LPU Route -> Provider: groq.cloud | Model: {groq_model}")
                try:
                    await groq_provider.connect()
                    groq_output = await groq_provider.generate(prompt=prompt, model=groq_model)
                    if groq_output.get("status") == "HEALTHY" and bool(groq_output.get("response")):
                        resp_preview = groq_output.get("response", "")[:60].replace("\n", " ")
                        print(f"[LLM] Groq LPU response received in {groq_output.get('latency_ms')}ms: \"{resp_preview}...\" ({len(groq_output.get('response', ''))} chars)")
                        return {
                            "status": "success",
                            "selected_model": groq_model,
                            "provider_id": "groq.cloud",
                            "score": score,
                            "task_category": task_cat,
                            "fallback_used": False,
                            "result": groq_output
                        }
                    else:
                        print(f"[LLM] Groq provider degraded ({groq_output.get('error')}). Falling back to next provider...")
                except Exception as e:
                    print(f"[LLM] Groq request failed ({e}). Falling back...")

        # Direct Gemini 3.6 Cloud Route (Primary when GEMINI_API_KEY is present)
        has_gemini_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        gemini_provider = self.registry.get("gemini.google")
        if not has_gemini_key and gemini_provider:
            has_gemini_key = bool(getattr(gemini_provider, "api_key", ""))

        if has_gemini_key and not require_offline:
            if gemini_provider:
                gemini_model = "gemini-3.6-flash"
                print(f"[LLM] Primary Cloud Route -> Provider: gemini.google | Model: {gemini_model}")

                try:
                    await gemini_provider.connect()
                    gem_output = await gemini_provider.generate(prompt=prompt, model=gemini_model)
                    if gem_output.get("status") == "HEALTHY" and bool(gem_output.get("response")):
                        resp_preview = gem_output.get("response", "")[:60].replace("\n", " ")
                        print(f"[LLM] Gemini response received: \"{resp_preview}...\" ({len(gem_output.get('response', ''))} chars)")
                        return {
                            "status": "success",
                            "selected_model": gemini_model,
                            "provider_id": "gemini.google",
                            "score": score,
                            "task_category": task_cat,
                            "fallback_used": False,
                            "result": gem_output
                        }
                    else:
                        print(f"[LLM] Gemini provider not active ({gem_output.get('error', 'no key')}). Falling back to local Ollama.")
                except Exception as e:
                    print(f"[LLM] Gemini request failed ({e}). Falling back to local Ollama.")



        # Direct OpenRouter Request or Cloud Priority
        if profile.provider_id == "openrouter.gateway" or any(w in prompt.lower() for w in ("openrouter", "use cloud", "use openrouter")):
            cloud_provider = self.registry.get("openrouter.gateway")
            if cloud_provider:
                cloud_model = getattr(cloud_provider, "default_model", "openrouter/free")
                print(f"[LLM] Direct Cloud Route -> Provider: openrouter.gateway | Model: {cloud_model}")
                try:
                    await cloud_provider.connect()
                    cloud_output = await cloud_provider.generate(prompt=prompt, model=cloud_model)
                    if cloud_output.get("status") == "AVAILABLE" and bool(cloud_output.get("response")):
                        resp_preview = cloud_output.get("response", "")[:60].replace("\n", " ")
                        print(f"[LLM] OpenRouter response received: \"{resp_preview}...\" ({len(cloud_output.get('response', ''))} chars)")
                        return {
                            "status": "success",
                            "selected_model": cloud_model,
                            "provider_id": "openrouter.gateway",
                            "score": score,
                            "task_category": task_cat,
                            "fallback_used": False,
                            "result": cloud_output
                        }
                    else:
                        print("[LLM] OpenRouter free-tier rate limit reached (50 req/day). Falling back to local Ollama.")
                except Exception as e:
                    print(f"[LLM] OpenRouter request failed ({e}). Falling back to local Ollama.")

        # 0.5 Distributed Worker Mesh Route (e.g. Friends' Gaming Laptops over Tailscale/LAN)
        from jarvisx.mesh.worker_router import get_worker_mesh_router
        mesh_router = get_worker_mesh_router()
        if mesh_router.has_active_workers():
            mesh_output = await mesh_router.execute_mesh_inference(
                prompt=prompt,
                model=profile.model_name,
                conversation=None,
                timeout_sec=2.5

            )

            if mesh_output.get("status") == "AVAILABLE" and bool(mesh_output.get("response")):
                resp_preview = mesh_output.get("response", "")[:60].replace("\n", " ")
                print(f"[LLM] Mesh Response received from {mesh_output.get('worker_name')}: \"{resp_preview}...\" ({len(mesh_output.get('response', ''))} chars)")
                return {
                    "status": "success",
                    "selected_model": mesh_output.get("model"),
                    "provider_id": mesh_output.get("provider_id"),
                    "score": score,
                    "task_category": task_cat,
                    "fallback_used": False,
                    "result": mesh_output
                }
            else:
                print(f"[LLM] Mesh workers unavailable. Falling back to local Ollama.")

        # 1. Primary Route: Local Ollama with NPU / Power Profile Adaptive Selection
        from jarvisx.hardware.npu_accelerator import get_npu_accelerator
        npu = get_npu_accelerator()

        provider = self.registry.get("ollama.local") or self.registry.get(profile.provider_id)
        try:
            await provider.connect()
        except Exception:
            pass

        installed = getattr(provider, "installed_models", [])

        if "qwen2.5-coder:1.5b" in installed and (task_cat in ("general", "chat", "summary") or npu.power_profile == "ECO"):
            chosen_model = "qwen2.5-coder:1.5b"
        elif "qwen2.5-coder:7b" in installed:
            chosen_model = "qwen2.5-coder:7b"
        elif "llama3.2:latest" in installed:
            chosen_model = "llama3.2:latest"
        else:
            chosen_model = profile.model_name

        print(f"[LLM] Provider: ollama.local")
        print(f"[LLM] Model: {chosen_model}")

        try:
            output = await provider.generate(prompt=prompt, model=chosen_model)
        except Exception as e:
            output = {
                "status": "NOT_AVAILABLE",
                "provider_id": "ollama.local",
                "model": chosen_model,
                "response": "",
                "error": str(e),
                "fallback_used": True
            }

        # Check if local provider succeeded
        is_success = (
            output.get("status") == "AVAILABLE"
            and bool(output.get("response"))
            and not output.get("fallback_used", False)
        )

        if is_success:
            resp_preview = output.get("response", "")[:60].replace("\n", " ")
            print(f"[LLM] Response received: \"{resp_preview}...\" ({len(output.get('response', ''))} chars)")

            self.history.record_outcome(
                provider_id="ollama.local",
                model_name=chosen_model,
                task_category=task_cat,
                success=True,
                latency=output.get("latency", 0.1),
                cost=output.get("cost", 0.0)
            )

            return {
                "status": "success",
                "selected_model": chosen_model,
                "provider_id": "ollama.local",
                "score": score,
                "task_category": task_cat,
                "fallback_used": False,
                "result": output
            }

        # 2. Local Provider Unavailable -> Fallback to Cloud (OpenRouter)
        if require_offline:
            print("[LLM] Ollama unavailable and offline required.")
            return {
                "status": "provider_unavailable",
                "primary": profile.provider_id,
                "fallback": None,
                "error": "Local LLM provider is offline and offline operation is required.",
                "result": output
            }

        print("[LLM] Ollama unavailable")
        print("[LLM] Falling back to OpenRouter")

        cloud_provider = self.registry.get("openrouter.gateway")
        if not cloud_provider:
            print("[LLM] OpenRouter provider not registered.")
            return {
                "status": "provider_unavailable",
                "primary": profile.provider_id,
                "fallback": "openrouter.gateway",
                "error": "OpenRouter provider is not registered in LLMRegistry.",
                "result": output
            }

        cloud_model = getattr(cloud_provider, "default_model", "openrouter/free")
        print(f"[LLM] Provider: openrouter.gateway")
        print(f"[LLM] Model: {cloud_model}")

        try:
            await cloud_provider.connect()
            cloud_output = await cloud_provider.generate(prompt=prompt, model=cloud_model)
        except Exception as e:
            cloud_output = {
                "status": "NOT_AVAILABLE",
                "provider_id": "openrouter.gateway",
                "model": cloud_model,
                "response": "",
                "error": str(e),
                "fallback_used": False
            }

        cloud_success = (
            cloud_output.get("status") == "AVAILABLE"
            and bool(cloud_output.get("response"))
        )

        if cloud_success:
            resp_preview = cloud_output.get("response", "")[:60].replace("\n", " ")
            print(f"[LLM] Response received: \"{resp_preview}...\" ({len(cloud_output.get('response', ''))} chars)")

            self.history.record_outcome(
                provider_id="openrouter.gateway",
                model_name=cloud_model,
                task_category=task_cat,
                success=True,
                latency=cloud_output.get("latency", 0.5),
                cost=cloud_output.get("cost", 0.0)
            )

            return {
                "status": "success",
                "selected_model": cloud_model,
                "provider_id": "openrouter.gateway",
                "score": score,
                "task_category": task_cat,
                "fallback_used": True,
                "result": cloud_output
            }

        # 3. Both Providers Failed
        err_msg = cloud_output.get("error", "Cloud provider request failed")
        print(f"[LLM] OpenRouter fallback failed: {err_msg}")
        print("[LLM] Both local and cloud providers unavailable")

        self.history.record_outcome(
            provider_id=profile.provider_id,
            model_name=chosen_model,
            task_category=task_cat,
            success=False,
            latency=output.get("latency", 0.1),
            cost=0.0
        )

        return {
            "status": "provider_unavailable",
            "primary": profile.provider_id,
            "fallback": "openrouter.gateway",
            "error": f"Both local Ollama and cloud OpenRouter failed. Error: {err_msg}",
            "result": cloud_output
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
