from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.missions.mission import Mission
from jarvisx.missions.mission_executor import MissionExecutor
from jarvisx.missions.mission_history import MissionHistory
from jarvisx.brain.brain_controller import BrainController
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor

class MissionManager:
    def __init__(
        self,
        brain: Optional[BrainController] = None,
        registry: Optional[CapabilityRegistry] = None,
        bus: Optional[HermesBus] = None
    ):
        self.brain = brain or BrainController()
        self.registry = registry or CapabilityRegistry()
        self.bus = bus or HermesBus()
        self.executor = MissionExecutor()
        self.history = MissionHistory()
        self.active_missions: Dict[str, Mission] = {}

    def get_descriptors(self) -> List[CapabilityDescriptor]:
        return [
            CapabilityDescriptor(
                id="mission.manager",
                name="Autonomous Mission Manager",
                version="1.0.0",
                author="Jarvis X",
                category="mission",
                supported_actions=["create_mission", "list_missions", "get_history"],
                handler=self.execute_mission_action
            )
        ]

    async def register(self, registry: CapabilityRegistry) -> None:
        self.registry = registry
        for desc in self.get_descriptors():
            await registry.register(desc)

    async def create_and_execute_mission(self, user_request: str) -> Dict[str, Any]:
        # 1. Brain processes intent
        brain_res = await self.brain.process_request(user_request)

        # 2. Create mission
        mission = Mission(
            title=user_request,
            user_request=user_request,
            intent=brain_res["intent"]["intent"],
            capability=brain_res["route"]["capability"],
            provider=brain_res["route"]["preferred_provider"],
            steps=[
                "Intent Analysis",
                "Architecture Design",
                "Provider Selection",
                "Code Generation",
                "Sandbox Testing",
                "GitHub PR Creation",
                "Memory Recording"
            ]
        )
        self.active_missions[mission.mission_id] = mission
        mission.status = "PLANNING"

        await self.bus.publish(Event(
            type="mission.created",
            source="mission_manager",
            payload={"mission_id": mission.mission_id, "intent": mission.intent}
        ))

        # 3. Execute mission
        result = await self.executor.execute(mission)

        # 4. Record history
        self.history.record(mission.mission_id, mission.status, result)

        await self.bus.publish(Event(
            type="mission.completed",
            source="mission_manager",
            payload={"mission_id": mission.mission_id, "status": mission.status}
        ))

        return {
            "mission": mission.to_dict(),
            "result": result
        }

    async def execute_mission_action(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "create_mission":
            req = kwargs.get("user_request", "")
            return await self.create_and_execute_mission(req)
        elif action == "list_missions":
            return {"missions": [m.to_dict() for m in self.active_missions.values()]}
        elif action == "get_history":
            return {"history": self.history.get_history()}
        raise NotImplementedError(f"Action '{action}' not supported.")
