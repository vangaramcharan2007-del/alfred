from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.coding.architecture_models import SystemArchitecture
from jarvisx.capabilities.coding.architecture_planner import ArchitecturePlanner
from jarvisx.capabilities.coding.adr_manager import ADRManager
from jarvisx.capabilities.coding.architecture_visualizer import ArchitectureVisualizer
from jarvisx.capabilities.coding.architecture_memory import ArchitectureMemory
from jarvisx.capabilities.coding.metrics import CodingMetrics

class ArchitectureAgent:
    def __init__(
        self,
        bus: Optional[HermesBus] = None,
        architecture_memory: Optional[ArchitectureMemory] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.bus = bus or HermesBus()
        self.arch_memory = architecture_memory or ArchitectureMemory()
        self.metrics = metrics or CodingMetrics()

        self.planner = ArchitecturePlanner()
        self.adr_manager = ADRManager(architecture_memory=self.arch_memory)
        self.visualizer = ArchitectureVisualizer()

    async def design_system(
        self,
        idea_description: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()

        # Event: Architect Started
        await self.bus.publish(Event(
            type="coding.architect.started",
            source="architecture_agent",
            payload={"idea": idea_description, "constraints": constraints or {}}
        ))

        # Step 1: System Architecture Proposal
        system_arch = self.planner.propose_architecture(idea_description, constraints)

        await self.bus.publish(Event(
            type="coding.architect.proposed",
            source="architecture_planner",
            payload={"project_name": system_arch.project_name, "components_count": len(system_arch.components)}
        ))

        # Step 2: Record ADRs
        adrs = []
        for dec in system_arch.decisions:
            adr = await self.adr_manager.create_adr(
                title=dec.decision,
                context=f"Architecture design for {system_arch.project_name}",
                decision=dec.decision,
                reasoning=dec.reasoning,
                consequences=dec.tradeoffs,
                alternatives=dec.alternatives_considered
            )
            adrs.append(adr)


            await self.bus.publish(Event(
                type="coding.architect.adr_created",
                source="adr_manager",
                payload=adr.to_dict()
            ))

        # Step 3: Generate Mermaid Diagrams
        component_diagram = self.visualizer.generate_component_diagram(system_arch)
        data_flow_diagram = self.visualizer.generate_data_flow_diagram(system_arch)
        dependency_diagram = self.visualizer.generate_dependency_diagram(system_arch)

        # Step 4: Update Observability Metrics
        self.metrics.record_codebase_intelligence(
            files=len(system_arch.components),
            deps=len(system_arch.data_flow),
            risks=len(system_arch.risks),
            arch_queries=1
        )
        self.metrics.record_task_completed(time.time() - start_time, success=True)

        return {
            "project_name": system_arch.project_name,
            "architecture": system_arch.to_dict(),
            "adrs": [a.to_dict() for a in adrs],
            "diagrams": {
                "component_diagram": component_diagram,
                "data_flow_diagram": data_flow_diagram,
                "dependency_diagram": dependency_diagram
            },
            "roadmap": [
                f"Phase 1: Provision {system_arch.technology_stack.get('backend', 'Backend Service')} foundation",
                f"Phase 2: Build components ({', '.join(c.name for c in system_arch.components)})",
                f"Phase 3: Integrate {system_arch.technology_stack.get('database', 'Database')} data models",
                f"Phase 4: Wire UI frontend client and AI layer APIs"
            ]
        }
