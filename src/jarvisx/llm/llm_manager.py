from __future__ import annotations
import time
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

class LLMManager:
    def __init__(
        self,
        router: Optional[LLMRouter] = None,
        bus: Optional[HermesBus] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.router = router or LLMRouter()
        self.bus = bus or HermesBus()
        self.metrics = metrics or CodingMetrics()

    def get_descriptors(self) -> List[CapabilityDescriptor]:
        return [
            CapabilityDescriptor(
                id="llm.gateway",
                name="Zero-Cost Local-First LLM Gateway",
                version="1.0.0",
                author="Jarvis X",
                category="llm",
                supported_actions=["generate", "stream", "fallback"],
                handler=self.execute_gateway_action
            ),
            CapabilityDescriptor(
                id="llm.routing",
                name="LLM Model Router",
                version="1.0.0",
                author="Jarvis X",
                category="routing",
                supported_actions=["select_model", "compare_models"],
                handler=self.execute_routing_action
            ),
            CapabilityDescriptor(
                id="llm.generation",
                name="LLM Code & Text Generator",
                version="1.0.0",
                author="Jarvis X",
                category="generation",
                supported_actions=["generate_code", "generate_reasoning"],
                handler=self.execute_generation_action
            ),
            CapabilityDescriptor(
                id="llm.analysis",
                name="LLM Hardware & Model Analyzer",
                version="1.0.0",
                author="Jarvis X",
                category="analysis",
                supported_actions=["detect_hardware", "health"],
                handler=self.execute_analysis_action
            )
        ]

    async def register(self, registry: CapabilityRegistry) -> None:
        for desc in self.get_descriptors():
            await registry.register(desc)

    async def execute_gateway_action(self, action: str, **kwargs) -> Dict[str, Any]:
        prompt = kwargs.get("prompt", "Hello Alfred")
        require_offline = kwargs.get("require_offline", False)
        start_t = time.time()

        await self.bus.publish(Event(
            type="llm.request.started",
            source="llm_manager",
            payload={"prompt": prompt[:50], "require_offline": require_offline}
        ))

        try:
            profile, score = self.router.select_model(prompt, require_offline=require_offline)
            await self.bus.publish(Event(
                type="llm.model.selected",
                source="llm_router",
                payload={"model": profile.model_name, "provider": profile.provider_id, "score": score}
            ))

            res = await self.router.route_request(prompt, require_offline=require_offline)
            duration = time.time() - start_t

            self.metrics.llm_requests += 1
            self.metrics.successful_requests += 1

            await self.bus.publish(Event(
                type="llm.response.completed",
                source="llm_manager",
                payload={"model": profile.model_name, "duration": round(duration, 3)}
            ))

            return res
        except Exception as e:
            self.metrics.llm_requests += 1
            self.metrics.failed_requests += 1
            await self.bus.publish(Event(
                type="llm.request.failed",
                source="llm_manager",
                payload={"error": str(e)}
            ))
            raise e

    async def execute_routing_action(self, action: str, **kwargs) -> Dict[str, Any]:
        prompt = kwargs.get("prompt", "Refactor module")
        if action == "select_model":
            profile, score = self.router.select_model(prompt, kwargs.get("require_offline", False))
            return {"selected_model": profile.to_dict(), "score": score}
        elif action == "compare_models":
            rankings = self.router.compare_models(prompt, count=kwargs.get("count", 3))
            return {"rankings": rankings}

        raise NotImplementedError(f"Action '{action}' is not supported.")

    async def execute_generation_action(self, action: str, **kwargs) -> Dict[str, Any]:
        prompt = kwargs.get("prompt", "Write Python function")
        return await self.execute_gateway_action("generate", prompt=prompt)

    async def execute_analysis_action(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "detect_hardware":
            hw = HardwareMonitor.get_hardware_specs()
            return {"hardware": hw.to_dict()}
        elif action == "health":
            providers = await self.router.registry.get_healthy_providers()
            return {"healthy_providers": [p.name for p in providers]}

        raise NotImplementedError(f"Action '{action}' is not supported.")
