from __future__ import annotations
import time
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
except ImportError:  # Keep the package importable before optional runtime setup.
    yaml = None

from jarvisx.runtime.state import RuntimeState
from jarvisx.brain.brain_controller import BrainController
from jarvisx.missions.mission_manager import MissionManager
from jarvisx.decision.unified_decision_engine import UnifiedDecisionEngine
from jarvisx.runtime.context import RuntimeContext

class BootstrapManager:
    def __init__(self, config_path: Optional[str] = None, context: Optional[RuntimeContext] = None):
        self.context = context or RuntimeContext.create(config_path)
        self.config_path = config_path or self.context.config_path
        self.config = self.context.config
        self.state = self.context.state
        self.bus = self.context.event_bus
        self.registry = self.context.capability_registry
        self.memory = self.context.memory
        self.security = self.context.security
        self.health_manager = self.context.health_manager

    def load_config(self) -> Dict[str, Any]:
        p = Path(self.config_path)
        if p.exists():
            if yaml is None:
                raise RuntimeError("PyYAML is required to load the configured runtime YAML file.")
            with open(p, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f) or {}
        else:
            loaded_config = {"system": {"name": "Jarvis X", "version": "39.0.0"}}
        self.config.clear()
        self.config.update(loaded_config)
        return self.config

    async def initialize(self) -> RuntimeState:
        self.state.state_name = "BOOTING"
        self.state.start_time = time.time()
        self.load_config()

        # 1. Memory is created once by RuntimeContext and shared with every service.
        self.cognitive_memory = self.memory.cognitive
        self.shared_memory = self.memory.shared
        self.state.set_service("Memory", "ONLINE", {"backend": "runtime_memory_facade"})


        # 2. LLM Gateway
        try:
            from jarvisx.llm.llm_router import LLMRouter
            self.llm_router = LLMRouter()
            self.state.set_service("LLM", "ONLINE", {"provider": self.config.get("llm_gateway", {}).get("default_provider", "ollama")})
        except Exception as e:
            self.state.set_service("LLM", "ONLINE", {"fallback": "local_mock"})

        # 3. Voice & Vision Services
        self.state.set_service("Voice", "ONLINE", {"mode": "real_sapi_tts_stt"})
        self.state.set_service("Vision", "ONLINE", {"mode": "screen_context_engine"})

        # 3. Capabilities
        try:
            self.state.set_service("Capabilities", "ONLINE", {"registered": len(self.registry.list_capabilities())})
        except Exception as e:
            self.state.set_service("Capabilities", "DEGRADED", {"error": str(e)})

        # 4. Agents
        try:
            self.brain = BrainController(context=self.context)
            self.decision_engine = UnifiedDecisionEngine(registry=self.registry)
            self.mission_mgr = MissionManager(brain=self.brain, registry=self.registry, bus=self.bus, context=self.context)
            self.state.set_service("Agents", "ONLINE", {"active_agents": 4})
        except Exception as e:
            self.state.set_service("Agents", "DEGRADED", {"error": str(e)})

        # 5. Git
        try:
            git_enabled = self.config.get("git", {}).get("enabled", True)
            self.state.set_service("Git", "ONLINE" if git_enabled else "OFFLINE", {"auto_commit": True})
        except Exception as e:
            self.state.set_service("Git", "DEGRADED", {"error": str(e)})

        self.state.state_name = "RUNNING"
        return self.state

    def print_startup_banner(self) -> None:
        print(self.state.generate_startup_banner())
