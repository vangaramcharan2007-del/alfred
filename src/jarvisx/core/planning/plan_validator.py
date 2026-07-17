from typing import List, Dict, Any, Tuple, Optional
from .dependency_graph import DependencyGraph


class PlanValidator:
    """Validates execution plans against the live ToolRegistry."""

    def __init__(self, registry=None):
        self._registry = registry

    @property
    def registry(self):
        if self._registry is None:
            from jarvisx.core.tools.tool_registry import ToolRegistry
            self._registry = ToolRegistry.get_instance()
        return self._registry

    def validate(self, plan: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validates the plan against the live registry.
        Returns (is_valid, error_message).
        """
        if not isinstance(plan, list):
            return False, "Plan must be a list of tasks"

        if len(plan) == 0:
            return False, "Plan must contain at least one task"

        task_ids = set()

        for idx, task in enumerate(plan):
            if not isinstance(task, dict):
                return False, f"Task at index {idx} must be a dictionary"

            required_keys = {"id", "description", "tool", "method", "args", "depends_on"}
            missing_keys = required_keys - set(task.keys())
            if missing_keys:
                return False, f"Task at index {idx} missing required keys: {missing_keys}"

            task_ids.add(task["id"])

            # Validate tool exists in registry
            if not self.registry.has_tool(task["tool"]):
                return False, f"Task '{task['id']}' uses unregistered tool: '{task['tool']}'"

            # Validate method exists on the tool
            if not self.registry.has_method(task["tool"], task["method"]):
                return False, f"Task '{task['id']}' uses unknown method '{task['method']}' on tool '{task['tool']}'"

        # Second pass: check dependencies exist
        for task in plan:
            for dep in task.get("depends_on", []):
                if dep not in task_ids:
                    return False, f"Task '{task['id']}' depends on nonexistent task: '{dep}'"

        # Check circular dependencies
        graph = DependencyGraph(plan)
        if graph.detect_cycles():
            return False, "Plan contains circular dependencies"

        return True, ""
