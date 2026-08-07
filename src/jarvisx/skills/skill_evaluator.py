"""Skill Evaluator, Ranking, and Retirement Engine for Phase 92.5."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.skills.models import SkillStatus
from jarvisx.skills.skill_metrics import SkillMetricsTracker
from jarvisx.skills.skill_registry import PersistentSkillRegistry


class SkillEvaluator:
    """Ranks alternative skills and automatically retires underperforming or failing capabilities."""

    def __init__(
        self,
        metrics_tracker: Optional[SkillMetricsTracker] = None,
        registry: Optional[PersistentSkillRegistry] = None
    ):
        self.metrics = metrics_tracker or SkillMetricsTracker()
        self.registry = registry or PersistentSkillRegistry()

    def rank_skills_by_reliability(self, skill_names: List[str]) -> List[str]:
        """Rank a list of skill candidates by their historical success rate and speed."""
        scored = []
        for name in skill_names:
            stats = self.metrics.get_skill_stats(name)
            if not stats:
                score = 0.5  # Neutral for untested
            else:
                score = stats.get("success_rate", 0.5) - (stats.get("average_runtime_sec", 0.0) * 0.01)
            scored.append((score, name))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored]

    def evaluate_and_retire_underperforming_skills(self, failure_threshold: float = 0.35) -> List[str]:
        """Retire/disable skills with failure rates higher than the threshold."""
        retired = []
        for name, stats in self.metrics.metrics.items():
            if stats["times_used"] >= 5 and stats["success_rate"] < (1.0 - failure_threshold):
                meta = self.registry.get_skill_metadata(name)
                if meta:
                    meta.status = SkillStatus.DISABLED
                    self.registry.register_installed_skill(meta)
                    retired.append(name)
                    print(f"[Skill Evaluator]: Retired unreliable skill '{name}' (Success Rate: {int(stats['success_rate']*100)}%).")
        return retired
