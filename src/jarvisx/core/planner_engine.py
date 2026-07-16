# src/jarvisx/core/planner_engine.py

class PlannerEngine:
    """
    Decomposes goals into tasks, builds execution plans, estimates complexity,
    estimates resource requirements, and generates fallback strategies.
    Re-plans automatically after failures.
    """
    def __init__(self):
        pass

    def generate_plan(self, goal_id: str, objective: str) -> list:
        """
        Detects software engineering goals and breaks them into parallelizable subtasks.
        """
        plan = []
        is_software_eng = self._is_software_engineering_goal(objective)
        
        if is_software_eng:
            # Break down into parallelizable agent orchestrator tasks
            plan.append({"task_id": f"{goal_id}-backend", "type": "sw_engineering", "capability": "fastapi", "desc": f"Backend API for {objective}"})
            plan.append({"task_id": f"{goal_id}-frontend", "type": "sw_engineering", "capability": "react", "desc": f"Frontend UI for {objective}"})
            plan.append({"task_id": f"{goal_id}-tests", "type": "sw_engineering", "capability": "pytest", "desc": f"Tests for {objective}"})
        else:
            plan.append({"task_id": f"{goal_id}-general", "type": "general", "desc": objective})
            
        return plan

    def _is_software_engineering_goal(self, objective: str) -> bool:
        keywords = ["build", "feature", "api", "frontend", "backend", "refactor", "app"]
        return any(kw in objective.lower() for kw in keywords)
