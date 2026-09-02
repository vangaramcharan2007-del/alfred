"""Agent Registry for Jarvis X.

Provides dynamic registration, capability discovery, and health diagnostics across all
operational workers to prevent hardcoded dependency coupling in Alfred's orchestration loop.
"""

from typing import Any, Dict, List, Optional
from jarvisx.agents.base import OperationalAgent
from jarvisx.architecture.contracts import AgentContract


class AgentRegistry:
    """Central workforce catalog managing registration, capability queries, and worker health."""

    def __init__(self):
        self._catalog: Dict[str, AgentContract] = {}

    def register(self, agent: AgentContract) -> None:
        """Register an active operational agent worker in the workforce catalog."""
        if not isinstance(agent, AgentContract):
            raise TypeError(f"Candidate {agent} does not fulfill standard AgentContract.")
        self._catalog[agent.name] = agent

    def unregister(self, name: str) -> Optional[AgentContract]:
        """Remove a worker from the active registry catalog."""
        return self._catalog.pop(name, None)

    def discover(self, capability: Optional[str] = None) -> List[str]:
        """Return agent names matching a desired operational capability."""
        if capability is None:
            return list(self._catalog.keys())
        matched = []
        for name, agent in self._catalog.items():
            if capability in agent.capabilities:
                matched.append(name)
        return matched

    def get_agent(self, name: str) -> Optional[AgentContract]:
        return self._catalog.get(name)

    def health(self) -> Dict[str, Any]:
        """Aggregate overall workforce diagnostic health and combined HSPW contribution."""
        status_map = {}
        total_hours_saved = 0.0
        active_workers = 0
        degraded_workers = 0

        for name, agent in self._catalog.items():
            st = agent.status()
            status_map[name] = st
            if st.get("health") == "degraded":
                degraded_workers += 1
            else:
                active_workers += 1

            if isinstance(agent, OperationalAgent):
                m = agent.metrics()
                total_hours_saved += float(m.get("hours_saved", 0.0))

        return {
            "total_workers": len(self._catalog),
            "active_healthy": active_workers,
            "degraded": degraded_workers,
            "workforce_status": ("nominal" if degraded_workers == 0 else "degraded"),
            "total_hours_saved": round(total_hours_saved, 2),
            "workers": status_map,
        }
