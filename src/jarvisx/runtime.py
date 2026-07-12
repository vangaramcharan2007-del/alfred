from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from jarvisx.agents.alfred import AlfredOrchestrator, IntentClassifier
from jarvisx.agents.edith import EdithAgent
from jarvisx.agents.registry import AgentRegistry
from jarvisx.agents.specialists import (
    CADAgent,
    DebugAgent,
    DeviceAgent,
    EditingAgent,
    MemoryAgent,
    PlannerAgent,
    ResearchAgent,
    ShadowBrokerAgent,
)
from jarvisx.core.health import HealthMonitor, HealthStatus
from jarvisx.core.hermes import HermesBus
from jarvisx.core.logging import StructuredLogger
from jarvisx.models.router import ModelRouter
from jarvisx.tools.device import DeviceTool
from jarvisx.tools.file_system import FileSystem
from jarvisx.tools.memory import LocalMemoryTool
from jarvisx.tools.missions import MissionTool
from jarvisx.tools.notifications import NotificationTool
from jarvisx.tools.personalization import PersonalizationTool
from jarvisx.tools.research import ResearchTool


@dataclass(frozen=True)
class JarvisRuntime:
    hermes: HermesBus
    registry: AgentRegistry
    alfred: AlfredOrchestrator
    health: HealthMonitor
    personalization: PersonalizationTool


def create_default_runtime(
    *,
    log_path: Optional[Path] = None,
    obsidian_vault: Optional[Path] = None,
) -> JarvisRuntime:
    logger = StructuredLogger(path=log_path)
    hermes = HermesBus(logger=logger)
    registry = AgentRegistry(logger=logger)

    memory_tool = LocalMemoryTool(vault_path=obsidian_vault, logger=logger)
    device_tool = DeviceTool()
    notification_tool = NotificationTool()
    research_tool = ResearchTool()
    personalization_tool = PersonalizationTool(memory_tool=memory_tool, logger=logger)
    mission_tool = MissionTool(
        memory_tool=memory_tool,
        personalization_tool=personalization_tool,
        logger=logger,
    )

    registry.register(MemoryAgent(tools={"memory": memory_tool}, logger=logger))
    registry.register(DeviceAgent(tools={"device": device_tool}, logger=logger))
    registry.register(ResearchAgent(tools={"research": research_tool}, logger=logger))
    registry.register(
        PlannerAgent(
            tools={"notification": notification_tool, "mission": mission_tool},
            logger=logger,
        )
    )
    registry.register(EditingAgent(tools={"file": FileSystem(root_dir=".")}, logger=logger))
    registry.register(CADAgent(tools={}, logger=logger))
    registry.register(ShadowBrokerAgent(tools={"research": research_tool}, logger=logger))
    registry.register(DebugAgent(tools={}, logger=logger))
    registry.register(
        EdithAgent(
            tools={
                "device": device_tool,
                "notification": notification_tool,
                "personalization": personalization_tool,
            },
            logger=logger,
        )
    )
    registry.bind(hermes)

    model_router = ModelRouter()
    alfred = AlfredOrchestrator(
        hermes=hermes,
        registry=registry,
        classifier=IntentClassifier(),
        model_router=model_router,
        personalization_tool=personalization_tool,
        logger=logger,
    )

    health = HealthMonitor()
    health.register("hermes", lambda: HealthStatus.ok("Hermes ready"))
    health.register("agent_registry", lambda: HealthStatus.ok(f"{len(registry)} agents registered"))
    health.register("memory_tool", memory_tool.health)
    health.register("personalization_tool", personalization_tool.health)
    health.register("mission_tool", mission_tool.health)
    health.register("device_tool", device_tool.health)
    health.register("research_tool", research_tool.health)

    return JarvisRuntime(
        hermes=hermes,
        registry=registry,
        alfred=alfred,
        health=health,
        personalization=personalization_tool,
    )
