from __future__ import annotations

from typing import Iterator, Optional

from jarvisx.agents.base import BaseAgent
from jarvisx.core.hermes import HermesBus
from jarvisx.core.logging import StructuredLogger


class AgentRegistry:
    def __init__(self, *, logger: Optional[StructuredLogger] = None) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._logger = logger or StructuredLogger()

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
