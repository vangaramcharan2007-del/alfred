from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.brain.intent_understanding import IntentUnderstanding
from jarvisx.brain.mission_router import MissionRouter
from jarvisx.brain.context_manager import ContextManager
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor

class BrainController:
    def __init__(
        self,
        registry: Optional[CapabilityRegistry] = None,
        bus: Optional[HermesBus] = None
    ):
        self.registry = registry or CapabilityRegistry()
        self.bus = bus or HermesBus()
        self.intent_engine = IntentUnderstanding()
        self.mission_router = MissionRouter()
        self.context_mgr = ContextManager()

    def get_descriptors(self) -> List[CapabilityDescriptor]:
        return [
            CapabilityDescriptor(
                id="brain.controller",
                name="Jarvis X Brain Controller",
                version="1.0.0",
                author="Jarvis X",
                category="brain",
                supported_actions=["process_request", "get_context"],
                handler=self.execute_brain_action
            )
        ]

    async def register(self, registry: CapabilityRegistry) -> None:
        self.registry = registry
        for desc in self.get_descriptors():
            await registry.register(desc)

    async def process_request(self, user_request: str) -> Dict[str, Any]:
        # 1. Intent Analysis
        intent = self.intent_engine.analyze_intent(user_request)
        await self.bus.publish(Event(
            type="brain.intent.analyzed",
            source="brain_controller",
            payload={"intent": intent["intent"], "confidence": intent["confidence"]}
        ))

        # 2. Mission Planning
        route = self.mission_router.route(intent["intent"])

        # 3. Capability Selection
        capability = route["capability"]

        # 4. Provider Selection
        provider = route["preferred_provider"]

        # 5. Context & Execution Setup
        ctx = self.context_mgr.push_context(user_request, intent, route)

        # 6. Learning & Event Dispatch
        await self.bus.publish(Event(
            type="brain.request.processed",
            source="brain_controller",
            payload={
                "request": user_request,
                "intent": intent["intent"],
                "capability": capability,
                "provider": provider
            }
        ))

        return {
            "request": user_request,
            "intent": intent,
            "route": route,
            "capability": capability,
            "provider": provider,
            "context_depth": len(self.context_mgr.context_stack),
            "pipeline_status": "READY"
        }


    async def execute_brain_action(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "process_request":
            req = kwargs.get("user_request", "")
            return await self.process_request(req)
        elif action == "get_context":
            return {"context": self.context_mgr.current_context(), "history_depth": len(self.context_mgr.context_stack)}
        raise NotImplementedError(f"Action '{action}' not supported by BrainController.")
