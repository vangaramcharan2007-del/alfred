"""Agent Registry — dynamic registration and capability-based discovery of agents."""
import logging
from typing import Dict, List, Optional
from .agent_identity import AgentIdentity

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Manages the pool of available agents. No hardcoded routing."""

    _instance: Optional["AgentRegistry"] = None

    def __init__(self):
        self._agents: Dict[str, AgentIdentity] = {}

    @classmethod
    def get_instance(cls) -> "AgentRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def register_agent(self, agent: AgentIdentity) -> None:
        self._agents[agent.agent_id] = agent
        agent.persist()
        logger.info(f"Registered agent: {agent.name} ({agent.agent_id}) role={agent.role}")

    def unregister_agent(self, agent_id: str) -> bool:
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[AgentIdentity]:
        return self._agents.get(agent_id)

    def get_agent_by_name(self, name: str) -> Optional[AgentIdentity]:
        for agent in self._agents.values():
            if agent.name == name:
                return agent
        return None

    def list_agents(self) -> List[AgentIdentity]:
        return list(self._agents.values())

    def discover_capable(self, capability: str) -> List[AgentIdentity]:
        """Find all agents that can handle a given capability and are available."""
        return [
            a for a in self._agents.values()
            if a.can_handle(capability) and a.is_available()
        ]

    def discover_by_role(self, role: str) -> List[AgentIdentity]:
        return [a for a in self._agents.values() if a.role == role]

    def find_replacement(self, failed_agent_id: str) -> Optional[AgentIdentity]:
        """Find an alternative agent with the same capabilities as the failed one."""
        failed = self._agents.get(failed_agent_id)
        if not failed:
            return None
        for agent in self._agents.values():
            if agent.agent_id == failed_agent_id:
                continue
            if agent.is_available() and agent.capabilities & failed.capabilities:
                return agent
        return None
