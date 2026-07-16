import logging
from typing import List, Dict, Set

logger = logging.getLogger(__name__)

class ExecutionGraph:
    """
    Directed Acyclic Graph (DAG) for managing task execution order and parallelization.
    """
    def __init__(self):
        # task_id -> task_data
        self.nodes: Dict[str, dict] = {}
        # task_id -> set of task_ids it depends on
        self.dependencies: Dict[str, Set[str]] = {}
        # task_id -> set of task_ids that depend on it
        self.dependents: Dict[str, Set[str]] = {}

    def add_node(self, task_id: str, data: dict):
        if task_id not in self.nodes:
            self.nodes[task_id] = data
            self.dependencies[task_id] = set()
            self.dependents[task_id] = set()

    def add_dependency(self, task_id: str, depends_on: str):
        if task_id in self.nodes and depends_on in self.nodes:
            self.dependencies[task_id].add(depends_on)
            self.dependents[depends_on].add(task_id)
            if self.detect_cycles():
                self.dependencies[task_id].remove(depends_on)
                self.dependents[depends_on].remove(task_id)
                raise ValueError(f"Cycle detected when adding dependency: {task_id} -> {depends_on}")

    def detect_cycles(self) -> bool:
        """Returns True if a cycle exists."""
        visited = set()
        path = set()

        def visit(node):
            if node in path:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            path.add(node)
            for dep in self.dependencies.get(node, []):
                if visit(dep):
                    return True
            path.remove(node)
            return False

        for node in self.nodes:
            if visit(node):
                return True
        return False

    def mark_completed(self, task_id: str):
        if task_id in self.nodes:
            self.nodes[task_id]["status"] = "completed"

    def mark_failed(self, task_id: str):
        if task_id in self.nodes:
            self.nodes[task_id]["status"] = "failed"
