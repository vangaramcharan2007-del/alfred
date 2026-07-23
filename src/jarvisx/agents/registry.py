from __future__ import annotations

from typing import Iterator, Optional
import sys

from jarvisx.agents.base import BaseAgent
from jarvisx.core.hermes import HermesBus
from jarvisx.core.logging import StructuredLogger


class AgentRegistry:
    def __init__(self, *, logger: Optional[StructuredLogger] = None) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._logger = logger or StructuredLogger()

    def discover(self, package_path: str = "src/jarvisx/agents") -> None:
        """Dynamically load and register all agent modules from a given directory."""
        import os, importlib.util, inspect
        from pathlib import Path
        
        path = Path(package_path)
        if not path.exists():
            return
            
        for file in path.rglob("*.py"):
            if file.name.startswith("__") or file.name in ("base.py", "registry.py", "alfred.py"):
                continue
                
            module_name = f"jarvisx.agents.{file.stem}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, str(file))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                            try:
                                instance = obj()
                                self.register(instance)
                            except Exception as e:
                                self._logger.write("warning", "agent.discovery_failed", error=str(e), class_name=name)
            except Exception as e:
                self._logger.write("warning", "agent.module_load_failed", error=str(e), file=str(file))

    def register(self, agent: BaseAgent) -> None:
        if agent.agent_id in self._agents:
            raise ValueError(f"Agent already registered: {agent.agent_id}")
        self._agents[agent.agent_id] = agent
        self._logger.write("info", "agent.registered", agent_id=agent.agent_id)

    def bind(self, hermes: HermesBus) -> None:
        for agent in self._agents.values():
            hermes.subscribe("agent.task.requested", agent.handle, subscriber_id=agent.agent_id)

    def get(self, agent_id: str) -> BaseAgent:
        return self._agents[agent_id]

    def maybe_get(self, agent_id: str) -> Optional[BaseAgent]:
        return self._agents.get(agent_id)

    def describe(self) -> list[dict[str, object]]:
        return [agent.describe() for agent in self._agents.values()]

    def __len__(self) -> int:
        return len(self._agents)

    def __iter__(self) -> Iterator[BaseAgent]:
        return iter(self._agents.values())
