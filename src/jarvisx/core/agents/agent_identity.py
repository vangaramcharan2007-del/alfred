"""Agent Identity — defines the structure, state, and capabilities of a Jarvis X agent."""
import json
import os
import time
import uuid
import logging
from typing import Dict, Any, List, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)

AGENT_STATE_DIR = "var/agent_state"


class AgentState(str, Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    FAILED = "FAILED"
    OFFLINE = "OFFLINE"


class AgentIdentity:
    """Represents a single autonomous agent with identity, capabilities, and lifecycle."""

    def __init__(
        self,
        name: str,
        role: str,
        capabilities: List[str],
        agent_id: Optional[str] = None,
        max_concurrent_objectives: int = 3,
    ):
        self.agent_id = agent_id or f"agent_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.role = role
        self.capabilities: Set[str] = set(capabilities)
        self.state = AgentState.IDLE
        self.active_objectives: List[str] = []
        self.max_concurrent_objectives = max_concurrent_objectives
        self.created_at = time.time()

    def can_handle(self, capability: str) -> bool:
        return capability in self.capabilities

    def is_available(self) -> bool:
        return (
            self.state in (AgentState.IDLE, AgentState.BUSY)
            and len(self.active_objectives) < self.max_concurrent_objectives
        )

    def assign_objective(self, objective_id: str):
        self.active_objectives.append(objective_id)
        self.state = AgentState.BUSY

    def release_objective(self, objective_id: str):
        if objective_id in self.active_objectives:
            self.active_objectives.remove(objective_id)
        if not self.active_objectives:
            self.state = AgentState.IDLE

    def mark_failed(self):
        self.state = AgentState.FAILED

    def mark_offline(self):
        self.state = AgentState.OFFLINE

    def recover(self):
        self.state = AgentState.IDLE
        self.active_objectives.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "capabilities": sorted(self.capabilities),
            "state": self.state.value,
            "active_objectives": list(self.active_objectives),
            "max_concurrent_objectives": self.max_concurrent_objectives,
            "created_at": self.created_at,
        }

    def persist(self):
        os.makedirs(AGENT_STATE_DIR, exist_ok=True)
        filepath = os.path.join(AGENT_STATE_DIR, f"{self.agent_id}.json")
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, agent_id: str) -> Optional["AgentIdentity"]:
        filepath = os.path.join(AGENT_STATE_DIR, f"{agent_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as f:
            data = json.load(f)
        agent = cls(
            name=data["name"],
            role=data["role"],
            capabilities=data["capabilities"],
            agent_id=data["agent_id"],
            max_concurrent_objectives=data.get("max_concurrent_objectives", 3),
        )
        agent.state = AgentState(data.get("state", "IDLE"))
        agent.active_objectives = data.get("active_objectives", [])
        agent.created_at = data.get("created_at", time.time())
        return agent
