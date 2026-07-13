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
from jarvisx.tools.computer_control import ComputerControlTool

from jarvisx.core.providers.provider_registry import ProviderRegistry
from jarvisx.core.providers.fallback_manager import FallbackManager
from jarvisx.core.providers.provider_router import ProviderRouter
from jarvisx.core.providers.startup_manager import StartupManager
from jarvisx.core.providers.health_monitor import ContinuousHealthMonitor
from jarvisx.core.proactive_monitor import ProactiveIntelligenceMonitor
from jarvisx.core.world_model import WorldModel

from jarvisx.core.providers.llm import OpenAIProvider, GeminiProvider, ClaudeProvider, GroqProvider, OpenRouterProvider, OllamaProvider, LlamaCppProvider, LocalGGUFProvider
from jarvisx.core.providers.tts import ElevenLabsProvider, PiperProvider, Pyttsx3Provider
from jarvisx.core.providers.stt import WhisperAPIProvider, FasterWhisperProvider, WhisperCppProvider
from jarvisx.core.providers.memory import SupabaseProvider, SQLiteProvider, LocalFilesProvider
from jarvisx.core.providers.vision import TesseractProvider, FutureOCRProvider


@dataclass(frozen=True)
class JarvisRuntime:
    hermes: HermesBus
    registry: AgentRegistry
    alfred: AlfredOrchestrator
    health: HealthMonitor
    personalization: PersonalizationTool
    provider_registry: ProviderRegistry
    fallback_manager: FallbackManager
    provider_router: ProviderRouter
    startup_manager: StartupManager
    continuous_health: ContinuousHealthMonitor
    proactive_monitor: ProactiveIntelligenceMonitor
    world_model: WorldModel


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
    world_model = WorldModel(op_db=op_db)
    
    mission_tool = MissionTool(
        memory_tool=memory_tool,
        personalization_tool=personalization_tool,
        logger=logger,
    )
    workflow_engine = WorkflowEngine(db=op_db)
    workflow_tool = WorkflowTool(engine=workflow_engine)
    computer_tool = ComputerControlTool(personalization=personalization_tool)

    registry.register(MemoryAgent(tools={"memory": memory_tool}, logger=logger))
    registry.register(DeviceAgent(tools={"device": device_tool, "computer": computer_tool}, logger=logger))
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

    # Provider Setup
    provider_registry = ProviderRegistry()
    
    # Register LLMs
    provider_registry.register(GeminiProvider())
    provider_registry.register(OpenAIProvider())
    provider_registry.register(ClaudeProvider())
    provider_registry.register(GroqProvider())
    provider_registry.register(OpenRouterProvider())
    provider_registry.register(OllamaProvider())
    provider_registry.register(LlamaCppProvider())
    provider_registry.register(LocalGGUFProvider())
    
    # Register TTS
    provider_registry.register(ElevenLabsProvider())
    provider_registry.register(PiperProvider())
    provider_registry.register(Pyttsx3Provider())
    
    # Register STT
    provider_registry.register(WhisperAPIProvider())
    provider_registry.register(FasterWhisperProvider())
    provider_registry.register(WhisperCppProvider())
    
    # Register MEMORY
    provider_registry.register(SupabaseProvider())
    provider_registry.register(SQLiteProvider())
    provider_registry.register(LocalFilesProvider())
    
    # Register VISION
    provider_registry.register(TesseractProvider())
    provider_registry.register(FutureOCRProvider())
    
    fallback_manager = FallbackManager(provider_registry)
    provider_router = ProviderRouter(fallback_manager)
    startup_manager = StartupManager(fallback_manager, health)
    continuous_health = ContinuousHealthMonitor(health, fallback_manager)
    proactive_monitor = ProactiveIntelligenceMonitor(hermes, personalization_tool, op_db)

    return JarvisRuntime(
        hermes=hermes,
        registry=registry,
        alfred=alfred,
        health=health,
        personalization=personalization_tool,
        provider_registry=provider_registry,
        fallback_manager=fallback_manager,
        provider_router=provider_router,
        startup_manager=startup_manager,
        continuous_health=continuous_health,
        proactive_monitor=proactive_monitor,
        world_model=world_model,
    )
