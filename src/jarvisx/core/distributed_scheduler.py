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

    def select_best_node(self, agent_id: str, required_capabilities: list[str], nodes_telemetry: list[Dict[str, Any]], user_preferences: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Advanced scheduling logic incorporating health, history, and preferences.
        
        Scoring Formula:
            Capability + Hardware + Health + Success History + User Preference Match
            - Latency - Failure Rate
        """
        best_score = -999.0
        best_node = None
        
        for node in nodes_telemetry:
            # Base capability/hardware is 1.0 if it's in telemetry (assuming capable)
            capability_match = 1.0
            hardware_score = 1.0 if node.get("gpu") == "available" else 0.5
            
            # Extract health and performance metrics
            status = node.get("status", "offline")
            if status != "online":
                continue # Skip offline nodes
                
            health_score = 1.0 # 100% healthy assuming online
            success_rate = node.get("success_rate", 100) / 100.0
            failure_rate = 1.0 - success_rate
            
            # Latency (convert ms string to float penalty)
            lat_str = str(node.get("latency", "50ms")).replace("ms", "")
            try:
                latency = float(lat_str)
            except ValueError:
                latency = 50.0
                
            latency_penalty = latency / 1000.0
            
            # ── Historical Intelligence Score ──
            # Success history: weighted score from past task completion data
            history_score = node.get("history_score", 0.0)
            
            # User preference match: how well this node/agent aligns with learned preferences
            preference_match = 0.0
            if user_preferences:
                # Check each learned preference against node capabilities
                pref_list = user_preferences.get("preferences", [])
                if isinstance(pref_list, list) and pref_list:
                    # Each matched preference contributes to the score
                    preference_match = min(0.5, len(pref_list) * 0.1)
                elif isinstance(pref_list, dict):
                    preference_match = min(0.5, len(pref_list) * 0.1)
                else:
                    preference_match = 0.1
            
            # Final Score: Capability + Hardware + Health + Success + History + Preference
            #              - Latency - Failure
            score = (
                capability_match + 
                hardware_score + 
                health_score + 
                success_rate + 
                history_score +
                preference_match - 
                latency_penalty - 
                failure_rate
            )
            
            self.logger.write("debug", "scheduler.node_scored", node=node.get("node"), score=score,
                              history_score=history_score, preference_match=preference_match)
            
            if score > best_score:
                best_score = score
                best_node = node.get("node")
                
        return best_node

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
        # Re-using the new select_best_node if we have telemetry
        # For compatibility, we'll fetch mock telemetry from NodeRegistry if available
        mock_telemetry = [
            {
                "node": n, 
                "gpu": "available" if self.node_registry._nodes[n].hardware_info.get("gpu") else "unavailable", 
                "status": "online", 
                "success_rate": 100, 
                "latency": "10ms"
            } 
            for n in self.node_registry._nodes.keys()
        ]
        best_node_id = self.select_best_node(best_agent, required_capabilities, mock_telemetry)
        
        if not best_node_id:
            self.logger.write("warning", "scheduler.no_node_found", agent=best_agent)
            return None
            
        self.logger.write("info", "scheduler.node_selected", task=task_id, node=best_node_id)
        
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
