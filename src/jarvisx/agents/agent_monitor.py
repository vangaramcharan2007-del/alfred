from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
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
        if agent_id in self._health_map:
            health = self._health_map[agent_id]
            if time.time() - health._last_heartbeat > 300 and health.status == "online":
                health.status = "offline"
            return health.to_dict()
        return None

    def list_health(self) -> List[Dict[str, object]]:
        """List health summaries for all registered agents."""
        return [self.get_agent_health(agent_id) for agent_id in self._health_map.keys() if self.get_agent_health(agent_id)]

    def monitor_node(self, node_id: str, status: str, latency: int, active_jobs: int = 0, gpu_available: bool = False) -> None:
        """Explicitly monitor a node's health and hardware availability."""
        # For this phase, we update all agents assigned to this node with the latest node metrics
        for health in self._health_map.values():
            if health.node == node_id:
                health.status = status
                health.latency = f"{latency}ms"
                health.gpu = "available" if gpu_available else "unavailable"
                health._last_heartbeat = time.time()
        
        # In a complete implementation we would store the node health in a separate map,
        # but for this iteration we can attach active_jobs to the logger event.
        self.logger.write("info", "monitor.node_updated", node=node_id, status=status, latency=latency, active_jobs=active_jobs)

    def monitor_agent(self, agent_id: str, success_rate: int) -> None:
        """Directly update an agent's success rate."""
        health = self._get_or_create(agent_id)
        health.success_rate = success_rate
        self.logger.write("info", "monitor.agent_updated", agent=agent_id, success_rate=success_rate)

    def get_network_health(self) -> Dict[str, Any]:
        """Aggregate the health of the entire node mesh."""
        total_nodes = len(set(h.node for h in self._health_map.values()))
        online_agents = sum(1 for h in self._health_map.values() if h.status == "online")
        
        # Provide the requested summary format alongside the mesh detail
        summaries = []
        for node in set(h.node for h in self._health_map.values()):
            node_agents = [h for h in self._health_map.values() if h.node == node]
            if node_agents:
                # Approximate node health from its agents
                first_agent = node_agents[0]
                is_healthy = first_agent.status == "online"
                latency_val = int(first_agent.latency.replace("ms", "")) if first_agent.latency.endswith("ms") else 0
                
                summaries.append({
                    "node": node,
                    "connection": "healthy" if is_healthy else "unhealthy",
                    "latency": latency_val,
                    "active_jobs": 0  # In a real implementation we would fetch from TaskManager
                })
        
        return {
            "total_nodes_tracked": total_nodes,
            "online_agents": online_agents,
            "node_summaries": summaries,
            "agent_mesh": self.list_health()
        }
