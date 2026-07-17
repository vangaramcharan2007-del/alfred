from typing import Dict, Any, List
from .task_decomposer import TaskDecomposer
from .plan_validator import PlanValidator
from jarvisx.core.providers.provider_router import ProviderRouter

class Planner:
    """Orchestrates the creation of execution plans."""
    
    def __init__(self, provider_router: ProviderRouter):
        self.decomposer = TaskDecomposer(provider_router)
        self.validator = PlanValidator()

    async def create_plan(self, objective: str, context: str = "") -> Dict[str, Any]:
        """Generates a validated execution plan for the given objective."""
        
        # Invoke task decomposition
        tasks = await self.decomposer.decompose(objective, context)
        
        # Validate the generated plan
        is_valid, err = self.validator.validate(tasks)
        if not is_valid:
            raise ValueError(f"Generated plan is invalid: {err}")
            
        # Estimate overall confidence based on tasks
        if tasks:
            confidence = sum(t.get("confidence", 0.0) for t in tasks) / len(tasks)
        else:
            confidence = 0.0
            
        return {
            "objective": objective,
            "confidence": round(confidence, 2),
            "steps": tasks
        }
