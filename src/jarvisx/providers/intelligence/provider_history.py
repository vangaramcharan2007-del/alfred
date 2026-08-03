from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class MissionOutcome:
    provider_id: str
    task_description: str
    success: bool
    runtime_seconds: float
    timestamp: float = field(default_factory=time.time)
    repo_path: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None

class ProviderHistoryManager:
    def __init__(self):
        self.history: List[MissionOutcome] = []
        self.language_preferences: Dict[str, str] = {}
        self.framework_preferences: Dict[str, str] = {}
        self.repo_preferences: Dict[str, str] = {}

    def record_outcome(
        self,
        provider_id: str,
        task_description: str,
        success: bool,
        runtime_seconds: float,
        repo_path: Optional[str] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None
    ) -> None:
        outcome = MissionOutcome(
            provider_id=provider_id,
            task_description=task_description,
            success=success,
            runtime_seconds=runtime_seconds,
            repo_path=repo_path,
            language=language,
            framework=framework
        )
        self.history.append(outcome)

        if success:
            if language:
                self.language_preferences[language.lower()] = provider_id
            if framework:
                self.framework_preferences[framework.lower()] = provider_id
            if repo_path:
                self.repo_preferences[repo_path] = provider_id

    def get_success_rate(self, provider_id: str) -> float:
        prov_outcomes = [h for h in self.history if h.provider_id == provider_id]
        if not prov_outcomes:
            return 0.95  # default neutral assumption
        successes = sum(1 for h in prov_outcomes if h.success)
        return successes / len(prov_outcomes)

    def get_preferred_provider_for_language(self, language: str) -> Optional[str]:
        return self.language_preferences.get(language.lower())

    def get_preferred_provider_for_framework(self, framework: str) -> Optional[str]:
        return self.framework_preferences.get(framework.lower())
