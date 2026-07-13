from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from jarvisx.agents.alfred import AlfredOrchestrator, IntentClassifier
from jarvisx.agents.edith import EdithAgent
from jarvisx.agents.plugins import PluginLoader
from jarvisx.agents.registry import AgentRegistry
from jarvisx.agents.xp import XPAgent
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
from jarvisx.agents.workflow import WorkflowAgent
from jarvisx.core.health import HealthMonitor, HealthStatus
from jarvisx.core.hermes import HermesBus
from jarvisx.core.logging import StructuredLogger
from jarvisx.core.workflows import WorkflowEngine
from jarvisx.models.router import ModelRouter
from jarvisx.tools.device import DeviceTool
from jarvisx.tools.file_system import FileSystem
from jarvisx.tools.memory import LocalMemoryTool
from jarvisx.tools.missions import MissionTool
from jarvisx.tools.notifications import NotificationTool
from jarvisx.tools.operational_db import OperationalDatabase
from jarvisx.tools.personalization import PersonalizationTool
from jarvisx.tools.research import ResearchTool
from jarvisx.tools.termux import TermuxTool
from jarvisx.tools.xp import XPTool
from jarvisx.tools.cad import CADTool
from jarvisx.tools.workflow import WorkflowTool


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
    op_db_path: Optional[Path] = None,
) -> JarvisRuntime:
    logger = StructuredLogger(path=log_path)
    hermes = HermesBus(logger=logger)
    registry = AgentRegistry(logger=logger)

    memory_tool = LocalMemoryTool(vault_path=obsidian_vault, logger=logger)
    op_db = OperationalDatabase(db_path=op_db_path or Path("var/jarvisx_op.db"), logger=logger)
    device_tool = DeviceTool()
    notification_tool = NotificationTool()
    research_tool = ResearchTool()
    personalization_tool = PersonalizationTool(memory_tool=memory_tool, logger=logger)
    xp_tool = XPTool(op_db=op_db, logger=logger)
    termux_tool = TermuxTool(logger=logger)
    cad_tool = CADTool(logger=logger)
    mission_tool = MissionTool(
        memory_tool=memory_tool,
        personalization_tool=personalization_tool,
        logger=logger,
    )
    workflow_engine = WorkflowEngine(db=op_db)
    workflow_tool = WorkflowTool(engine=workflow_engine)

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
    registry.register(CADAgent(tools={"cad": cad_tool}, logger=logger))
    registry.register(ShadowBrokerAgent(tools={"research": research_tool}, logger=logger))
    registry.register(DebugAgent(tools={"termux": termux_tool}, logger=logger))
    registry.register(
        EdithAgent(
            tools={
                "notification": notification_tool,
                "personalization": personalization_tool,
                "termux": termux_tool,
            },
            logger=logger,
        )
    )
    registry.register(XPAgent(tools={"xp": xp_tool}, logger=logger))
    registry.register(WorkflowAgent(engine=workflow_engine))
    
    # Load dynamic agents
    plugins_dir = Path(__file__).resolve().parent / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    PluginLoader(registry, logger=logger).load_from_directory(plugins_dir)

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
    health.register("xp_tool", xp_tool.health)

    return JarvisRuntime(
        hermes=hermes,
        registry=registry,
        alfred=alfred,
        health=health,
        personalization=personalization_tool,
    )
