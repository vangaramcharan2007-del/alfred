from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from jarvisx.core.logging import StructuredLogger

@dataclass
class AgentHealth:
    agent: str
    node: str = "local"
    status: str = "offline"
    gpu: str = "unavailable"
    latency: str = "0ms"
    success_rate: int = 100
    
    # Internal tracking
    _total_executions: int = 0
    _successful_executions: int = 0
    _last_heartbeat: float = 0.0
    _last_execution_time: float = 0.0

    def to_dict(self) -> Dict[str, object]:
        return {
            "node": self.node,
            "agent": self.agent,
            "gpu": self.gpu,
            "latency": self.latency,
            "status": self.status,
            "success_rate": self.success_rate
        }

class AgentMonitor:
    """
    Tracks the health, availability, and performance of distributed agents.
    Prepares for multi-node setups by tracking node assignments and local hardware state.
    """
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.logger = logger or StructuredLogger()
        self._health_map: Dict[str, AgentHealth] = {}
        
    def _get_or_create(self, agent_id: str, node: str = "local") -> AgentHealth:
        if agent_id not in self._health_map:
            self._health_map[agent_id] = AgentHealth(agent=agent_id, node=node)
        return self._health_map[agent_id]

    def register_heartbeat(self, agent_id: str, node: str = "local", gpu_available: bool = False) -> None:
        """Register a heartbeat from an agent node."""
        health = self._get_or_create(agent_id, node)
        health._last_heartbeat = time.time()
        health.status = "online"
        health.gpu = "available" if gpu_available else "unavailable"
        
    def record_success(self, agent_id: str, execution_time_ms: int) -> None:
        """Record a successful agent execution."""
        health = self._get_or_create(agent_id)
        health._total_executions += 1
        health._successful_executions += 1
        health._last_execution_time = execution_time_ms
        health.latency = f"{execution_time_ms}ms"
        
        # Calculate success rate
        health.success_rate = int((health._successful_executions / health._total_executions) * 100)
        
    def record_failure(self, agent_id: str, execution_time_ms: int) -> None:
        """Record a failed agent execution."""
        health = self._get_or_create(agent_id)
        health._total_executions += 1
        health._last_execution_time = execution_time_ms
        health.latency = f"{execution_time_ms}ms"
        
        # Calculate success rate
        health.success_rate = int((health._successful_executions / health._total_executions) * 100)
        self.logger.write("warning", "agent_monitor.failure_recorded", agent_id=agent_id, success_rate=health.success_rate)

    def get_agent_health(self, agent_id: str) -> Optional[Dict[str, object]]:
        """Get the current health dictionary for a specific agent."""
        # Simple offline detection (no heartbeat in 5 minutes)
        if agent_id in self._health_map:
            health = self._health_map[agent_id]
            if time.time() - health._last_heartbeat > 300 and health.status == "online":
                health.status = "offline"
            return health.to_dict()
        return None

    def list_health(self) -> List[Dict[str, object]]:
        """List health summaries for all registered agents."""
        return [self.get_agent_health(agent_id) for agent_id in self._health_map.keys()]
