import time
from typing import Dict, Any, Optional
from jarvisx.core.logging import StructuredLogger
from jarvisx.network.event_bus import DistributedEventBus

class MeshMetrics:
    """
    Provides complete observability over the Cognitive Agent Network.
    Tracks throughput, latencies, failure rates, and memory storage events.
    """
    def __init__(self, event_bus: DistributedEventBus, logger: Optional[StructuredLogger] = None):
        self.logger = logger or StructuredLogger()
        self.event_bus = event_bus
        
        # State counters
        self.nodes_online: int = 0
        self.active_agents: int = 0
        self.tasks_completed: int = 0
        self.tasks_failed: int = 0
        self.recovery_events: int = 0
        self.memory_growth: int = 0
        
        # Latency tracking
        self._latency_sum: float = 0.0
        self._latency_count: int = 0
        
        # Subscribe to relevant events
        self.event_bus.subscribe("agent.connection.connected", self._on_node_connected)
        self.event_bus.subscribe("agent.connection.disconnected", self._on_node_disconnected)
        self.event_bus.subscribe("task.completed", self._on_task_completed)
        self.event_bus.subscribe("task.failed", self._on_task_failed)
        self.event_bus.subscribe("recovery.task_migrated", self._on_recovery)
        self.event_bus.subscribe("cognitive_memory.stored", self._on_memory_stored)

    def _on_node_connected(self, payload: Dict[str, Any]) -> None:
        self.nodes_online += 1
        
    def _on_node_disconnected(self, payload: Dict[str, Any]) -> None:
        self.nodes_online = max(0, self.nodes_online - 1)
        
    def _on_task_completed(self, payload: Dict[str, Any]) -> None:
        self.tasks_completed += 1
        if "latency" in payload:
            try:
                lat = float(str(payload["latency"]).replace("ms", ""))
                self._latency_sum += lat
                self._latency_count += 1
            except ValueError:
                pass
                
    def _on_task_failed(self, payload: Dict[str, Any]) -> None:
        self.tasks_failed += 1
        
    def _on_recovery(self, payload: Dict[str, Any]) -> None:
        self.recovery_events += 1
        
    def _on_memory_stored(self, payload: Dict[str, Any]) -> None:
        self.memory_growth += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Returns a snapshot of the current mesh telemetry."""
        total_tasks = self.tasks_completed + self.tasks_failed
        success_rate = 100.0
        if total_tasks > 0:
            success_rate = (self.tasks_completed / total_tasks) * 100.0
            
        avg_latency = 0.0
        if self._latency_count > 0:
            avg_latency = self._latency_sum / self._latency_count
            
        return {
            "nodes_online": self.nodes_online,
            "active_tasks": total_tasks, # For this snapshot, just reflecting total processed
            "success_rate": round(success_rate, 2),
            "average_latency": round(avg_latency, 2),
            "recovery_events": self.recovery_events,
            "memory_growth": self.memory_growth
        }
