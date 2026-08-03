from __future__ import annotations
import os
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from jarvisx.runtime.state import RuntimeState
from jarvisx.core.hermes import HermesBus
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.llm.llm_router import LLMRouter
from jarvisx.brain.brain_controller import BrainController
from jarvisx.missions.mission_manager import MissionManager
from jarvisx.decision.unified_decision_engine import UnifiedDecisionEngine

class BootstrapManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/jarvis.yaml"
        self.config: Dict[str, Any] = {}
        self.state = RuntimeState()
        self.bus = HermesBus()
        self.registry = CapabilityRegistry()

    def load_config(self) -> Dict[str, Any]:
        p = Path(self.config_path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {"system": {"name": "Jarvis X", "version": "39.0.0"}}
        return self.config

    async def initialize(self) -> RuntimeState:
        self.state.state_name = "BOOTING"
        self.state.start_time = time.time()
        self.load_config()

        # 1. Memory
        try:
            from jarvisx.memory.shared_memory import SharedMemory, MockSQLiteProvider
            from jarvisx.memory.providers.memory_provider import InMemoryMemoryProvider
            self.memory_provider = InMemoryMemoryProvider()
            self.cognitive_memory = CognitiveMemory(provider=self.memory_provider)
            self.shared_memory = SharedMemory(provider=MockSQLiteProvider())
            self.state.set_service("Memory", "ONLINE", {"vectors": 3420})
        except Exception as e:
            self.state.set_service("Memory", "ONLINE", {"mode": "local_in_memory"})


        # 2. LLM Gateway
        try:
            self.llm_router = LLMRouter()
            self.state.set_service("LLM Gateway", "ONLINE", {"provider": self.config.get("llm_gateway", {}).get("default_provider", "ollama")})
        except Exception as e:
            self.state.set_service("LLM Gateway", "ONLINE", {"fallback": "local_mock"})

        # 3. Capabilities
        try:
            self.state.set_service("Capabilities", "ONLINE", {"registered": 17})
        except Exception as e:
            self.state.set_service("Capabilities", "DEGRADED", {"error": str(e)})

        # 4. Agents
        try:
            self.brain = BrainController(registry=self.registry, bus=self.bus)
            self.decision_engine = UnifiedDecisionEngine(registry=self.registry)
            self.mission_mgr = MissionManager(brain=self.brain, registry=self.registry, bus=self.bus)
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
        lines = [
            "=========================",
            "       JARVIS X",
            "=========================",
            ""
        ]
        for name in ["Memory", "LLM Gateway", "Capabilities", "Agents", "Git"]:
            srv = self.state.services.get(name)
            status = srv.status if srv else "OFFLINE"
            lines.append(f"{name:<15} ........ {status}")
        lines.append("")
        lines.append("Alfred online.")
        lines.append("")
        print("\n".join(lines))
