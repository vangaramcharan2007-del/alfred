import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from jarvisx.nodes.worker_node import WorkerNode
from jarvisx.core.logging import StructuredLogger

class NodeRegistry:
    """
    In-memory registry for discovering and tracking WorkerNodes.
    Provides logic to score and find the best node for a specific capability.
    """
    def __init__(self, logger: Optional[StructuredLogger] = None):
        self._nodes: Dict[str, WorkerNode] = {}
        self.logger = logger or StructuredLogger()

    def register_node(self, node: WorkerNode) -> None:
        """Register a new WorkerNode in the mesh."""
        self._nodes[node.node_id] = node
        self.logger.write("info", "registry.node_registered", node=node.node_id, agents=node.available_agents)

    def remove_node(self, node_id: str) -> None:
        """Remove a WorkerNode from the mesh."""
        if node_id in self._nodes:
            del self._nodes[node_id]
            self.logger.write("info", "registry.node_removed", node=node_id)

    def get_available_nodes(self) -> List[WorkerNode]:
        """Return a list of all online nodes."""
        online_nodes = []
        for node in self._nodes.values():
            # Basic timeout check: 5 minutes without heartbeat = offline
            if time.time() - node._last_heartbeat > 300:
                node.status = "offline"
            if node.status == "online":
                online_nodes.append(node)
        return online_nodes

    def update_heartbeat(self, node_id: str, latency: int = 0) -> None:
        """Update a node's heartbeat to keep it marked as online."""
        if node_id in self._nodes:
            self._nodes[node_id].heartbeat(latency)

    def find_best_node(self, target_agent: str, required_hardware: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Score available nodes that can run the target agent.
        Returns a sorted list of dictionaries with node metadata and score.
        """
        results = []
        online_nodes = self.get_available_nodes()
        
        for node in online_nodes:
            if target_agent not in node.available_agents:
                continue
                
            # Base score for capability match
            score = 1.0
            
            # Hardware check
            gpu_present = bool(node.hardware_info.get("gpu"))
            if required_hardware and required_hardware.get("gpu") and not gpu_present:
                score -= 0.5  # Heavy penalty for missing requested hardware
                
            # Latency penalty (small deduction per ms)
            score -= (node.network_latency * 0.001)
            
            # Simulated failure rate penalty (future integration with AgentMonitor)
            # score -= failure_rate
            
            results.append({
                "node": node.node_id,
                "score": round(max(0.0, min(1.0, score)), 2),
                "gpu": gpu_present,
                "latency": node.network_latency
            })
            
        return sorted(results, key=lambda x: x["score"], reverse=True)
