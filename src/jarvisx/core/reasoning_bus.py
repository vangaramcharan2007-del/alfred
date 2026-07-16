# src/jarvisx/core/reasoning_bus.py

import logging

logger = logging.getLogger("ReasoningBus_Hermes")

class CollaborativeReasoningBus:
    """
    Hermes Router: Routes tasks according to execution strategy
    (single_agent, workforce, hybrid).
    """
    def __init__(self, workforce_manager=None):
        self.workforce_manager = workforce_manager

    def publish_thought(self, agent_id: str, thought_payload: dict):
        pass

    def route_task(self, task: dict):
        """
        Determines the Execution Mode based on task complexity and type.
        """
        execution_mode = self._determine_execution_mode(task)
        logger.info(f"Routing task {task['task_id']} via mode: {execution_mode}")
        
        if execution_mode == "single_agent":
            self._route_to_single_agent(task)
        elif execution_mode == "workforce":
            self._route_to_workforce(task)
        elif execution_mode == "hybrid":
            self._route_to_hybrid(task)
            
    def _determine_execution_mode(self, task: dict) -> str:
        desc = task.get("desc", "").lower()
        if "rename" in desc or "minor fix" in desc:
            return "single_agent"
        if "build" in desc or "feature" in desc or "system" in desc:
            return "workforce"
        return "hybrid"

    def _route_to_single_agent(self, task: dict):
        logger.info(f"Executing {task['task_id']} via single-agent distributed executor.")

    def _route_to_workforce(self, task: dict):
        logger.info(f"Dispatching {task['task_id']} to Agent Orchestrator Workforce...")
        if self.workforce_manager:
            import asyncio
            asyncio.create_task(self.workforce_manager.dispatch_task(
                task["task_id"], task["desc"], task.get("capability", "python")
            ))

    def _route_to_hybrid(self, task: dict):
        logger.info(f"Dispatching {task['task_id']} via Hybrid mode...")
        self._route_to_single_agent(task)
        self._route_to_workforce(task)
