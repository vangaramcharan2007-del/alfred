"""Architectural Contracts and Agent Interfaces for Jarvis X.

Establishes layer ownership, dependency rules, forbidden import patterns, and the
canonical base class for all future agents.
"""

import abc
from typing import Any, Dict, List

from jarvisx.architecture.layers import LAYER_ORDER


class ArchitectureContract:
    """Defines ownership, allowable dependency flow, and explicit restrictions across layers."""

    OWNERSHIP: Dict[str, str] = {
        "human": "User preferences, configurations, and environment interaction settings.",
        "alfred": "Central intelligence, lifecycle orchestration, mission routing, and governance.",
        "agents": "Specialized autonomous workers (Brain, Memory, Planner, Voice, Vision, Hands, Research).",
        "capabilities": "Reusable tools, command executions, and modular abilities exposed to agents.",
        "infrastructure": "External adapters, database persistence, observability, and deployment models.",
        "interface": "Human-facing interaction surfaces, terminal interfaces, and CLI commands.",
    }

    # Explicit forbidden dependency pairings across specific packages to protect system boundaries
    FORBIDDEN_IMPORTS: List[Dict[str, str]] = [
        {
            "source": "memory",
            "target": "runtime",
            "reason": "Memory must not import high-level orchestration runtime.",
        },
        {
            "source": "automation",
            "target": "brain",
            "reason": "Action/Voice/Vision layers must not couple directly to reasoning engine.",
        },
        {
            "source": "tools",
            "target": "missions",
            "reason": "Low-level tools must not depend on mission planning abstractions.",
        },
        {
            "source": "adapters",
            "target": "ui",
            "reason": "Infrastructure database/adapters must never reference UI or presentation code.",
        },
        {
            "source": "adapters",
            "target": "interface",
            "reason": "Infrastructure database/adapters must never reference CLI interface code.",
        },
    ]

    @classmethod
    def is_valid_layer_dependency(cls, source_layer: str, target_layer: str) -> bool:
        """Verifies if importing target_layer from source_layer adheres to architectural flow.

        Dependency flow is top-down (or within the same layer), plus interface layers
        can invoke alfred/agents to execute user actions.
        """
        if source_layer == target_layer:
            return True
        if source_layer == "interface":
            # Interface layer drives the application by invoking Alfred and Agent capabilities
            return True

        try:
            source_idx = LAYER_ORDER.index(source_layer)
            target_idx = LAYER_ORDER.index(target_layer)
            return source_idx <= target_idx
        except ValueError:
            return True


class AgentContract(abc.ABC):
    """Canonical abstract base class defining the mandatory interface for all future agents.

    Every operational agent controlled by Alfred must implement these standardized attributes and behaviors.
    """

    name: str
    purpose: str
    capabilities: List[str]

    def __init__(self, name: str, purpose: str, capabilities: List[str]):
        self.name = name
        self.purpose = purpose
        self.capabilities = capabilities

    @abc.abstractmethod
    def execute(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Execute an autonomous task payload and return standard status output."""
        pass

    @abc.abstractmethod
    def status(self) -> Dict[str, Any]:
        """Return current operational status, health metrics, and active resource utilization."""
        pass

    @abc.abstractmethod
    def report(self) -> str:
        """Generate a clean, human-readable summary report of completed activities and state."""
        pass
