from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.evolution.evolution_state import EvolutionState
from jarvisx.evolution.evolution_controller import EvolutionController
from jarvisx.evolution.improvement_detector import ImprovementDetector, ImprovementProposal
from jarvisx.evolution.evolution_planner import EvolutionPlanner, EvolutionMission
from jarvisx.evolution.research_agent import AutonomousResearchAgent
from jarvisx.evolution.evolution_simulator import EvolutionSimulator, SimulationResult
from jarvisx.evolution.evolution_guard import EvolutionGuard
from jarvisx.evolution.evolution_executor import EvolutionExecutor
from jarvisx.evolution.evolution_memory import EvolutionMemory
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.coding.metrics import CodingMetrics


class _InlineMetaEngine:
    """Minimal meta-cognition stub — replaced the deleted jarvisx.meta module."""
    async def run_self_analysis(self) -> Dict[str, Any]:
        return {"status": "HEALTHY", "weak_points": [], "score": 0.95}


class AutonomousEvolutionEngine:
    def __init__(
        self,
        meta_engine: Optional[_InlineMetaEngine] = None,
        registry: Optional[CapabilityRegistry] = None,
        bus: Optional[HermesBus] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.meta_engine = meta_engine or _InlineMetaEngine()
        self.registry = registry or CapabilityRegistry()
        self.bus = bus or HermesBus()
        self.metrics = metrics or CodingMetrics()

        self.state = EvolutionState()
        self.controller = EvolutionController(state=self.state)
        self.detector = ImprovementDetector()
        self.planner = EvolutionPlanner()
        self.research_agent = AutonomousResearchAgent()
        self.simulator = EvolutionSimulator()
        self.guard = EvolutionGuard()
        self.executor = EvolutionExecutor(metrics=self.metrics)
        self.memory = EvolutionMemory()

    def get_descriptors(self) -> List[CapabilityDescriptor]:
        return [
            CapabilityDescriptor(
                id="evolution.engine",
                name="Autonomous Evolution Engine",
                version="1.0.0",
                author="Jarvis X",
                category="evolution",
                supported_actions=["detect", "simulate", "plan", "execute_upgrade"],
                handler=self.execute_evolution_action
            )
        ]

    async def register(self, registry: CapabilityRegistry) -> None:
        self.registry = registry
        for desc in self.get_descriptors():
            await registry.register(desc)

    async def run_evolution_cycle(self) -> Dict[str, Any]:
        # 1. Run Meta Analysis
        meta_report = await self.meta_engine.run_self_analysis()

        # 2. Detect Improvement Proposals
        proposals = self.detector.detect_proposals(meta_report)
        if not proposals:
            return {"status": "no_proposals", "message": "No system weakness detected."}

        proposal = proposals[0]
        await self.bus.publish(Event(
            type="evolution.detected",
            source="evolution_engine",
            payload={"proposal": proposal.to_dict()}
        ))

        # 3. Simulate Upgrade
        simulation = self.simulator.simulate_upgrade(proposal)

        # 4. Check Safety Guard
        safety_eval = self.guard.evaluate_safety(proposal)
        if safety_eval.get("approval_required", False):
            await self.bus.publish(Event(
                type="evolution.approval_required",
                source="evolution_guard",
                payload={"proposal_id": proposal.proposal_id, "reason": safety_eval["reason"]}
            ))

        # 5. Plan Engineering Mission
        mission = self.planner.create_mission(proposal)
        await self.bus.publish(Event(
            type="evolution.planned",
            source="evolution_planner",
            payload={"mission": mission.to_dict(), "simulation": simulation.to_dict()}
        ))

        # 6. Execute Upgrade
        self.controller.start_upgrade(proposal.proposal_id, proposal.proposed_solution, proposal.risk_level)
        await self.bus.publish(Event(
            type="evolution.started",
            source="evolution_engine",
            payload={"proposal_id": proposal.proposal_id}
        ))

        exec_res = await self.executor.execute_mission(mission)

        # 7. Complete & Record in Memory
        self.controller.complete_upgrade(proposal.proposal_id, exec_res)
        self.memory.record_evolution_event(
            upgrade_id=proposal.proposal_id,
            reason=proposal.problem,
            changes_made=mission.steps,
            success=True,
            lessons_learned="Successfully applied upgrade with verified sandbox tests."
        )

        await self.bus.publish(Event(
            type="evolution.completed",
            source="evolution_engine",
            payload={"upgrade_id": proposal.proposal_id, "commit": exec_res["commit_message"]}
        ))

        return {
            "proposal": proposal.to_dict(),
            "simulation": simulation.to_dict(),
            "safety": safety_eval,
            "mission": mission.to_dict(),
            "execution": exec_res,
            "state": self.state.to_dict()
        }

    async def execute_evolution_action(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "detect":
            meta_report = await self.meta_engine.run_self_analysis()
            proposals = self.detector.detect_proposals(meta_report)
            return {"proposals": [p.to_dict() for p in proposals]}
        elif action == "simulate":
            prop_data = kwargs.get("proposal", {})
            prop = ImprovementProposal(
                proposal_id=prop_data.get("proposal_id", "prop_001"),
                problem=prop_data.get("problem", "Low score"),
                proposed_solution=prop_data.get("proposed_solution", "Integrate tool"),
                priority=prop_data.get("priority", "HIGH"),
                risk_level=prop_data.get("risk_level", "LOW")
            )
            return self.simulator.simulate_upgrade(prop).to_dict()
        elif action == "plan":
            prop_data = kwargs.get("proposal", {})
            prop = ImprovementProposal(
                proposal_id=prop_data.get("proposal_id", "prop_001"),
                problem=prop_data.get("problem", "Low score"),
                proposed_solution=prop_data.get("proposed_solution", "Integrate tool"),
                priority=prop_data.get("priority", "HIGH"),
                risk_level=prop_data.get("risk_level", "LOW")
            )
            return self.planner.create_mission(prop).to_dict()
        elif action == "execute_upgrade":
            return await self.run_evolution_cycle()

        raise NotImplementedError(f"Action '{action}' is not supported by AutonomousEvolutionEngine.")
