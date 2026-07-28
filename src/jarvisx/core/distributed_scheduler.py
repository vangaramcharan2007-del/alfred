from typing import Dict, Any, Optional
import uuid

from jarvisx.agents.capability_registry import CapabilityRegistry
from jarvisx.nodes.node_registry import NodeRegistry
from jarvisx.network.agent_protocol import TaskRequest
from jarvisx.core.logging import StructuredLogger

class DistributedScheduler:
    """
    Coordinates task execution by bridging the CapabilityRegistry (Agent Selection)
    and NodeRegistry (Machine Selection).
    """
    def __init__(self, capability_registry: CapabilityRegistry, node_registry: NodeRegistry, logger: Optional[StructuredLogger] = None):
        self.capability_registry = capability_registry
        self.node_registry = node_registry
        self.logger = logger or StructuredLogger()

    async def dispatch(self, trace_id: str, required_capabilities: list[str], payload: Dict[str, Any], required_hardware: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Dispatches a task based on requested capabilities.
        Returns a job_id if successfully dispatched.
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # 1. Query CapabilityRegistry (Agent Selection)
        agent_scores = self.capability_registry.discover_capability(required_capabilities)
        if not agent_scores:
            self.logger.write("warning", "scheduler.no_agent_found", capabilities=required_capabilities)
            return None
            
        best_agent = agent_scores[0]["agent"]
        self.logger.write("info", "scheduler.agent_selected", task=task_id, agent=best_agent)
        
        # 2. Query NodeRegistry (Machine Selection)
        node_scores = self.node_registry.find_best_node(best_agent, required_hardware=required_hardware)
        if not node_scores:
            self.logger.write("warning", "scheduler.no_node_found", agent=best_agent)
            return None
            
        best_node_id = node_scores[0]["node"]
        self.logger.write("info", "scheduler.node_selected", task=task_id, node=best_node_id, score=node_scores[0]["score"])
        
        # 3. Dispatch Task
        request = TaskRequest(
            task_id=task_id,
            trace_id=trace_id,
            agent_id=best_agent,
            required_capabilities=required_capabilities,
            payload=payload
        )
        
        # Retrieve the actual node instance from registry to call execute_task
        # In a real network setup, this would be an AgentProtocol proxy
        node = self.node_registry._nodes.get(best_node_id)
        if not node:
            return None
            
        job_id = await node.execute_task(request)
        return job_id
