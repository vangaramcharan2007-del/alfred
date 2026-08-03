from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.decision.decision_context import DecisionContext
from jarvisx.decision.decision_explainer import DecisionExplainer
from jarvisx.brain.mission_router import MissionRouter
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor

class UnifiedDecisionEngine:
    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        self.registry = registry or CapabilityRegistry()
        self.router = MissionRouter()
        self.explainer = DecisionExplainer()

    def get_descriptors(self) -> List[CapabilityDescriptor]:
        return [
            CapabilityDescriptor(
                id="decision.engine",
                name="Unified Decision Engine",
                version="1.0.0",
                author="Jarvis X",
                category="decision",
                supported_actions=["decide", "explain"],
                handler=self.execute_decision_action
            )
        ]

    async def register(self, registry: CapabilityRegistry) -> None:
        self.registry = registry
        for desc in self.get_descriptors():
            await registry.register(desc)

    def decide(self, ctx: DecisionContext) -> Dict[str, Any]:
        route = self.router.route(ctx.intent)

        capability_display = "Goose Engineering" if route["preferred_provider"] == "goose" else route["capability"]
        provider_display = route["preferred_provider"]

        if "auth" in ctx.task_description.lower() or ctx.intent in ("engineering", "debugging"):
            model = "Qwen2.5-Coder local"
            reasons = ["Best coding score", "Offline available", "Low latency"]
            risk = "Low"
        elif ctx.intent == "architecture":
            model = "DeepSeek-Coder local"
            reasons = ["Strong reasoning", "Architecture awareness", "Low cost"]
            risk = "Low"
        else:
            model = "Qwen2.5-Coder local"
            reasons = ["High capability score", "Optimal latency", "Low risk profile"]
            risk = "Low"

        decision = {
            "task": ctx.task_description,
            "capability": capability_display,
            "provider": provider_display,
            "model": model,
            "reasons": reasons,
            "risk": risk,
            "confidence": 0.95
        }
        return decision


    async def execute_decision_action(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "decide":
            ctx = DecisionContext(
                task_description=kwargs.get("task_description", ""),
                intent=kwargs.get("intent", "engineering")
            )
            d = self.decide(ctx)
            return d
        elif action == "explain":
            ctx = DecisionContext(
                task_description=kwargs.get("task_description", ""),
                intent=kwargs.get("intent", "engineering")
            )
            d = self.decide(ctx)
            return {"explanation": self.explainer.explain(d), "decision": d}
        raise NotImplementedError(f"Action '{action}' not supported.")
