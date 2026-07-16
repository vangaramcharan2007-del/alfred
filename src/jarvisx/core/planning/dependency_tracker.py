from typing import List, Dict
from .execution_graph import ExecutionGraph

class DependencyTracker:
    """
    Determines task readiness based on the ExecutionGraph state.
    """
    def __init__(self, graph: ExecutionGraph):
        self.graph = graph

    def get_task_state(self, task_id: str) -> str:
        """
        Returns 'completed', 'running', 'blocked', or 'ready'.
        """
        task = self.graph.nodes.get(task_id)
        if not task:
            return "unknown"
            
        status = task.get("status", "created")
        if status in ("completed", "failed", "cancelled", "running"):
            return status

        # If any dependency is NOT completed, this task is blocked.
        for dep_id in self.graph.dependencies.get(task_id, []):
            dep_task = self.graph.nodes.get(dep_id, {})
            if dep_task.get("status") != "completed":
                return "blocked"
                
        return "ready"

    def get_ready_tasks(self) -> List[str]:
        ready = []
        for task_id in self.graph.nodes:
            if self.get_task_state(task_id) == "ready":
                ready.append(task_id)
        return ready

    def get_blocking_tasks(self, task_id: str) -> List[str]:
        """Returns the specific tasks currently blocking this task."""
        blocking = []
        for dep_id in self.graph.dependencies.get(task_id, []):
            dep_task = self.graph.nodes.get(dep_id, {})
            if dep_task.get("status") != "completed":
                blocking.append(dep_id)
        return blocking
