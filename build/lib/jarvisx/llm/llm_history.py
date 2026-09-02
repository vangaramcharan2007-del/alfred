from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class LLMGenerationOutcome:
    provider_id: str
    model_name: str
    task_category: str
    success: bool
    latency: float
    cost: float = 0.0
    timestamp: float = field(default_factory=time.time)
    repo_path: Optional[str] = None

class LLMHistoryManager:
    def __init__(self):
        self.history: List[LLMGenerationOutcome] = []
        self.preferred_models: Dict[str, str] = {}  # task_category -> model_name
        self.repo_preferences: Dict[str, str] = {}

    def record_outcome(
        self,
        provider_id: str,
        model_name: str,
        task_category: str,
        success: bool,
        latency: float,
        cost: float = 0.0,
        repo_path: Optional[str] = None
    ) -> None:
        outcome = LLMGenerationOutcome(
            provider_id=provider_id,
            model_name=model_name,
            task_category=task_category,
            success=success,
            latency=latency,
            cost=cost,
            repo_path=repo_path
        )
        self.history.append(outcome)

        if success:
            self.preferred_models[task_category.lower()] = model_name
            if repo_path:
                self.repo_preferences[repo_path] = model_name

    def get_success_rate(self, provider_id: str, model_name: str) -> float:
        matching = [h for h in self.history if h.provider_id == provider_id and h.model_name == model_name]
        if not matching:
            return 0.95
        successes = sum(1 for h in matching if h.success)
        return successes / len(matching)

    def get_preferred_model_for_task(self, task_category: str) -> Optional[str]:
        return self.preferred_models.get(task_category.lower())
