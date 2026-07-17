from typing import Dict, Any, List
from .task_decomposer import TaskDecomposer
from .plan_validator import PlanValidator
from jarvisx.core.providers.provider_router import ProviderRouter


class Planner:
    """Orchestrates the creation of execution plans grounded in live tool capabilities."""

    def __init__(self, provider_router: ProviderRouter, registry=None):
        self._registry = registry
        self.decomposer = TaskDecomposer(provider_router, registry=registry)
        self.validator = PlanValidator(registry=registry)

    async def create_plan(self, objective: str, context: str = "") -> Dict[str, Any]:
        """Generates a validated execution plan for the given objective."""

        # Invoke task decomposition (with injected capabilities)
        tasks = await self.decomposer.decompose(objective, context)

        # Validate the generated plan against the live registry
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
