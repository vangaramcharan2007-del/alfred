from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.providers.intelligence.provider_profiler import ProviderProfile
from jarvisx.providers.intelligence.provider_capabilities import TaskCategory, TaskClassifier

class ProviderScorer:
    def compute_score(
        self,
        profile: ProviderProfile,
        task_description: str,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        require_offline: bool = False,
        historical_success: Optional[float] = None
    ) -> float:
        score = 0.0

        # Health check filter
        if profile.health_status == "UNHEALTHY":
            return 0.0
        elif profile.health_status == "DEGRADED":
            score += 0.05
        else:
            score += 0.15

        # Task classification compatibility
        task_cat = TaskClassifier.classify_task(task_description)
        if task_cat.value in profile.supported_tasks:
            score += 0.25
        elif any(t.lower() in task_description.lower() for t in profile.supported_tasks):
            score += 0.15

        # Language compatibility
        if language:
            lang_lower = language.lower()
            if lang_lower in [l.lower() for l in profile.supported_languages]:
                score += 0.20
            else:
                score -= 0.10

        # Framework compatibility
        if framework:
            fw_lower = framework.lower()
            if fw_lower in [f.lower() for f in profile.supported_frameworks]:
                score += 0.15
            else:
                score -= 0.05

        # Historical success rate factor
        success_rate = historical_success if historical_success is not None else profile.average_success_rate
        score += 0.15 * max(0.0, min(1.0, success_rate))

        # Latency & Speed factor
        if profile.average_latency <= 0.3:
            score += 0.05

        # Cost factor
        if profile.average_cost == 0.0:
            score += 0.05

        # Offline requirement check
        if require_offline:
            if profile.offline_support:
                score += 0.10
            else:
                score -= 0.30

        return max(0.0, min(1.0, score))
