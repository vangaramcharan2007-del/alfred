"""Agent Dispatcher for Jarvis X.

Serves as the execution bridge between Alfred (Layer 2) and autonomous workers (Layer 3),
enforcing interface compliance via AgentContract without violating boundary rules.
"""

from typing import Any, Dict, List, Optional
from jarvisx.architecture.contracts import AgentContract


class AgentDispatcher:
    """Central registry and router for directing mission tasks to canonical agent modules."""

    def __init__(self):
        self._agents: Dict[str, AgentContract] = {}

    def register_agent(self, agent: AgentContract) -> None:
        """Register an active agent worker adhering to the standard AgentContract interface."""
        if not isinstance(agent, AgentContract):
            raise TypeError(f"Agent {agent} does not implement AgentContract.")
        self._agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional[AgentContract]:
        return self._agents.get(name)

    def list_agents(self) -> Dict[str, List[str]]:
        return {name: agent.capabilities for name, agent in self._agents.items()}

    def assign(self, task_description: str, agent_name: str, **kwargs: Any) -> Dict[str, Any]:
        """Assign a structured task payload directly to the designated agent."""
        agent = self._agents.get(agent_name)
        if not agent:
            return {
                "agent": agent_name,
                "status": "error",
                "error": f"Agent '{agent_name}' is not registered in the dispatcher workforce.",
            }

        payload = {"description": task_description, "parameters": kwargs}
        try:
            result = agent.execute(payload)
            return {
                "agent": agent_name,
                "status": result.get("status", "completed"),
                "output": result.get("output", str(result)),
            }
        except Exception as e:
            return {"agent": agent_name, "status": "error", "error": str(e)}
