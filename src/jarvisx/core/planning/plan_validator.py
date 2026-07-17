from typing import List, Dict, Any, Tuple
from .dependency_graph import DependencyGraph

class PlanValidator:
    """Validates execution plans for schema compliance and logic errors."""
    
    # Valid tools that Jarvis X execution layer supports
    VALID_TOOLS = {
        "file_ops",
        "command_executor",
        "python_executor",
        "git_ops",
        "app_launcher",
        "browser_manager",
        "desktop_controller",
        "vision_layer",
        "mouse_controller",
        "keyboard_controller",
        "window_manager"
    }

    @staticmethod
    def validate(plan: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validates the plan. Returns (is_valid, error_message).
        """
        if not isinstance(plan, list):
            return False, "Plan must be a list of tasks"
            
        task_ids = set()
        
        for idx, task in enumerate(plan):
            if not isinstance(task, dict):
                return False, f"Task at index {idx} must be a dictionary"
                
            required_keys = {"id", "description", "tool", "method", "args", "depends_on"}
            missing_keys = required_keys - set(task.keys())
            if missing_keys:
                return False, f"Task at index {idx} missing required keys: {missing_keys}"
                
            task_ids.add(task["id"])
            
            if task["tool"] not in PlanValidator.VALID_TOOLS:
                return False, f"Task {task['id']} uses unknown tool: {task['tool']}"
                
        # Second pass: check dependencies exist
        for task in plan:
            for dep in task.get("depends_on", []):
                if dep not in task_ids:
                    return False, f"Task {task['id']} depends on nonexistent task: {dep}"
                    
        # Check circular dependencies
        graph = DependencyGraph(plan)
        if graph.detect_cycles():
            return False, "Plan contains circular dependencies"
            
        return True, ""
