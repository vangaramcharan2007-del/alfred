from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import threading
import datetime

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
    GreetingAgent,
    MemoryAgent,
    PlannerAgent,
    ResearchAgent,
    ShadowBrokerAgent,
)
from jarvisx.agents.workflow import WorkflowAgent
from jarvisx.agents.capability_agent import CapabilityAgent
from jarvisx.agents.video_skill import VideoSkillAgent
from jarvisx.agents.friday import FridayAgent
from jarvisx.core.context import DeviceContext
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

from jarvisx.core.capabilities.registry import SystemCapabilityRegistry
from jarvisx.core.capabilities.runtime import CapabilityRuntime

from jarvisx.core.providers.provider_registry import ProviderRegistry
from jarvisx.core.providers.fallback_manager import FallbackManager
from jarvisx.core.providers.provider_router import ProviderRouter
from jarvisx.core.providers.startup_manager import StartupManager
from jarvisx.core.providers.health_monitor import ContinuousHealthMonitor
from jarvisx.core.proactive_monitor import ProactiveIntelligenceMonitor
from jarvisx.core.world_model import WorldModel
from jarvisx.core.shutdown_manager import ShutdownManager
from jarvisx.core.configuration import ConfigurationManager
from jarvisx.core.backup_manager import BackupManager

from jarvisx.core.providers.llm import OpenAIProvider, GeminiProvider, ClaudeProvider, GroqProvider, OpenRouterProvider, OllamaProvider, LlamaCppProvider, LocalGGUFProvider
from jarvisx.core.providers.tts import ElevenLabsProvider, Pyttsx3Provider, XTTSv2Provider, F5TTSProvider
from jarvisx.core.providers.voice_manager import VoiceManager
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
    workflow_tool: WorkflowTool
    config_manager: ConfigurationManager
    backup_manager: BackupManager
    capability_registry: SystemCapabilityRegistry
    capability_runtime: CapabilityRuntime
    voice_manager: VoiceManager
    data_dir: Path
    shutdown_manager: ShutdownManager = field(init=False)
    _cron_stop_event: threading.Event = field(init=False)
    _cron_thread: threading.Thread = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "shutdown_manager", ShutdownManager(self))
        object.__setattr__(self, "_cron_stop_event", threading.Event())
        object.__setattr__(self, "_cron_thread", threading.Thread(target=self._cron_loop, daemon=True, name="JarvisCron"))
        self._cron_thread.start()
        
    def _cron_loop(self) -> None:
        """Background thread for daily maintenance tasks."""
        last_backup_date = None
        while not self._cron_stop_event.is_set():
            now = datetime.datetime.now()
            today = now.date()
            
            # Run daily tasks at 3:00 AM
            if now.hour == 3 and today != last_backup_date:
                try:
                    self.backup_manager.run_scheduled_backup()
                    # Assuming access to tools via registry or direct injection if needed
                    last_backup_date = today
                except Exception as e:
                    # Log error via alfred/logger if available
                    pass
            
            # Check every minute
            self._cron_stop_event.wait(60)

    def shutdown(self) -> None:
        self.shutdown_manager.shutdown()
        self.continuous_health.stop()
        self.proactive_monitor.stop()
        self._cron_stop_event.set()
        if hasattr(self, '_cron_thread') and self._cron_thread.is_alive():
            self._cron_thread.join(timeout=2.0)


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
    config_manager = ConfigurationManager(op_db=op_db)
    device_tool = DeviceTool()
    notification_tool = NotificationTool()
    research_tool = ResearchTool()
    personalization_tool = PersonalizationTool(memory_tool=memory_tool, config_manager=config_manager, logger=logger)
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
    backup_manager = BackupManager(data_dir=Path("data"), backup_dir=Path("backups"))
    device_context = DeviceContext()

    registry.register(GreetingAgent(logger=logger))
    registry.register(MemoryAgent(tools={"memory": memory_tool}, logger=logger))
    registry.register(DeviceAgent(tools={"device": device_tool, "computer": computer_tool, "context": device_context}, logger=logger))
    registry.register(ResearchAgent(tools={"research": research_tool}, logger=logger))
    registry.register(
        PlannerAgent(
            tools={"notification": notification_tool, "mission": mission_tool},
            logger=logger,
        )
    )
    registry.register(FridayAgent(tools={"file": FileSystem(root_dir="."), "computer": computer_tool}, logger=logger))
    registry.register(EditingAgent(tools={"file": FileSystem(root_dir=".")}, logger=logger))
    registry.register(CADAgent(tools={"cad": cad_tool}, logger=logger))
    registry.register(ShadowBrokerAgent(tools={"research": research_tool}, logger=logger))
    registry.register(DebugAgent(tools={"termux": termux_tool}, logger=logger))
    registry.register(VideoSkillAgent(logger=logger))
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
    
    # Bootstrap Capability Runtime
    capability_registry = SystemCapabilityRegistry(logger=logger)
    capabilities_plugins_dir = Path(__file__).resolve().parent / "core" / "capabilities" / "providers"
    capability_registry.discover_plugins(capabilities_plugins_dir)
    capability_runtime = CapabilityRuntime(registry=capability_registry, logger=logger)
    
    # Register Capability Agent
    registry.register(CapabilityAgent(runtime=capability_runtime, logger=logger))
    
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
    provider_registry.register(Pyttsx3Provider())
    provider_registry.register(XTTSv2Provider())
    provider_registry.register(F5TTSProvider())
    
    # Initialize VoiceManager
    voice_manager = VoiceManager(provider_registry=provider_registry)
    voice_manager.register("Alfred", provider="pyttsx3", voice_id="default")
    voice_manager.register("Friday", provider="pyttsx3", voice_id=r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
    voice_manager.register("Edith", provider="elevenlabs", voice_id="female_voice")
    
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
    startup_manager = StartupManager(fallback_manager, health, config_manager)
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
        workflow_tool=workflow_tool,
        config_manager=config_manager,
        backup_manager=backup_manager,
        capability_registry=capability_registry,
        capability_runtime=capability_runtime,
        voice_manager=voice_manager,
        data_dir=Path("data"),
    )
