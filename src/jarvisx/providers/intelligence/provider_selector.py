from __future__ import annotations
import time
from typing import Dict, Any, List, Optional, Tuple
from jarvisx.providers.intelligence.provider_profiler import ProviderProfiler, ProviderProfile
from jarvisx.providers.intelligence.provider_scoring import ProviderScorer
from jarvisx.providers.intelligence.provider_history import ProviderHistoryManager
from jarvisx.providers.intelligence.provider_scheduler import ProviderScheduler
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.coding.metrics import CodingMetrics

class ProviderSelector:
    def __init__(
        self,
        profiler: Optional[ProviderProfiler] = None,
        scorer: Optional[ProviderScorer] = None,
        history: Optional[ProviderHistoryManager] = None,
        scheduler: Optional[ProviderScheduler] = None,
        bus: Optional[HermesBus] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.profiler = profiler or ProviderProfiler()
        self.scorer = scorer or ProviderScorer()
        self.history = history or ProviderHistoryManager()
        self.scheduler = scheduler or ProviderScheduler()
        self.bus = bus or HermesBus()
        self.metrics = metrics or CodingMetrics()

    def get_descriptor(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            id="provider.intelligence",
            name="Provider Intelligence Engine",
            version="1.0.0",
            author="Jarvis X",
            category="core",
            supported_actions=["provider.selection", "provider.analysis", "provider.routing"],
            handler=self.handle_action
        )

    async def register(self, registry: CapabilityRegistry) -> None:
        descriptor = self.get_descriptor()
        await registry.register(descriptor)

    async def handle_action(self, action: str, **kwargs) -> Any:
        task_desc = kwargs.get("task_description", "Generic Engineering Task")
        lang = kwargs.get("language")
        fw = kwargs.get("framework")

        if action == "provider.selection":
            profile, score = await self.select_provider(task_desc, language=lang, framework=fw)
            return {"selected_provider": profile.to_dict(), "score": score}
        elif action == "provider.analysis":
            rankings = self.select_multiple(task_desc, count=5, language=lang, framework=fw)
            return {"rankings": [{"provider": p.to_dict(), "score": s} for p, s in rankings]}
        elif action == "provider.routing":
            profile = self.load_balance(task_desc, language=lang, framework=fw)
            return {"routed_provider": profile.to_dict()}

        raise NotImplementedError(f"Action '{action}' is not supported by ProviderSelector.")

    async def select_provider(
        self,
        task_description: str,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        require_offline: bool = False
    ) -> Tuple[ProviderProfile, float]:
        start_time = time.time()
        profiles = self.profiler.list_profiles()

        best_profile: Optional[ProviderProfile] = None
        best_score = -1.0

        for p in profiles:
            hist_success = self.history.get_success_rate(p.provider_id)
            score = self.scorer.compute_score(
                profile=p,
                task_description=task_description,
                language=language,
                framework=framework,
                require_offline=require_offline,
                historical_success=hist_success
            )

            # Affinity bonus
            if language and self.history.get_preferred_provider_for_language(language) == p.provider_id:
                score += 0.05

            if score > best_score:
                best_score = score
                best_profile = p

        if not best_profile:
            best_profile = profiles[0]
            best_score = 0.5

        latency = time.time() - start_time
        self.metrics.provider_selections += 1
        self.metrics.selection_latency = (self.metrics.selection_latency + latency) / 2.0 if self.metrics.selection_latency > 0 else latency

        await self.bus.publish(Event(
            type="provider.selected",
            source="provider_selector",
            payload={"provider_id": best_profile.provider_id, "score": round(best_score, 3), "task": task_description}
        ))

        return best_profile, round(best_score, 3)

    def select_multiple(
        self,
        task_description: str,
        count: int = 3,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        require_offline: bool = False
    ) -> List[Tuple[ProviderProfile, float]]:
        ranked = []
        for p in self.profiler.list_profiles():
            hist_success = self.history.get_success_rate(p.provider_id)
            score = self.scorer.compute_score(
                profile=p,
                task_description=task_description,
                language=language,
                framework=framework,
                require_offline=require_offline,
                historical_success=hist_success
            )
            ranked.append((p, round(score, 3)))

        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:count]

    async def fallback_provider(
        self,
        current_provider_id: str,
        task_description: str,
        language: Optional[str] = None,
        framework: Optional[str] = None
    ) -> Tuple[ProviderProfile, float]:
        self.metrics.provider_failovers += 1

        await self.bus.publish(Event(
            type="provider.rejected",
            source="provider_selector",
            payload={"provider_id": current_provider_id, "reason": "Failed execution / Fallback triggered"}
        ))

        multiple = self.select_multiple(task_description, count=5, language=language, framework=framework)
        for p, s in multiple:
            if p.provider_id != current_provider_id:
                return p, s

        # Return default if all else fails
        fallback_p = self.profiler.get_profile("local_coding_agent") or self.profiler.list_profiles()[0]
        return fallback_p, 0.5

    async def reroute(
        self,
        failed_provider_id: str,
        task_description: str,
        language: Optional[str] = None,
        framework: Optional[str] = None
    ) -> Tuple[ProviderProfile, float]:
        self.metrics.provider_reroutes += 1

        await self.bus.publish(Event(
            type="provider.rerouted",
            source="provider_selector",
            payload={"failed_provider_id": failed_provider_id, "task": task_description}
        ))

        return await self.fallback_provider(failed_provider_id, task_description, language, framework)

    def load_balance(
        self,
        task_description: str,
        language: Optional[str] = None,
        framework: Optional[str] = None
    ) -> ProviderProfile:
        multiple = self.select_multiple(task_description, count=5, language=language, framework=framework)
        for p, s in multiple:
            if self.scheduler.is_provider_available(p.provider_id):
                return p
        return multiple[0][0]
