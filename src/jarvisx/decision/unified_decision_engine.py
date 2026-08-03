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

        # Model selection
        model = "qwen2.5-coder:7b"
        model_reasons = ["Best coding score", "Offline available", "Low latency"]

        if ctx.intent == "architecture":
            model = "deepseek-coder:6.7b"
            model_reasons = ["Strong reasoning", "Architecture awareness", "Low cost"]

        decision = {
            "task": ctx.task_description,
            "capability": route["capability"],
            "provider": route["preferred_provider"],
            "model": model,
            "reasons": model_reasons,
            "risk": "LOW",
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
