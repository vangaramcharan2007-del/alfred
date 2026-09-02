"""Mission Prioritization Scoring Engine for Jarvis X (Layer 2 - Planning).

Scores priority using:
priority = deadline_urgency + goal_importance + dependency_impact + user_preference
"""

import math
from typing import Any, Dict


class Prioritizer:
    """Zero-fluff production mission prioritization scoring engine."""

    def compute_priority_score(
        self,
        days_until_deadline: float = 7.0,
        goal_importance: float = 5.0,
        downstream_dependencies_count: int = 0,
        user_preference_weight: float = 1.0,
    ) -> Dict[str, Any]:
        """Compute priority score: priority = deadline_urgency + goal_importance + dependency_impact + user_preference."""
        # 1. Deadline Urgency Score (Exponential scale as deadline approaches)
        days_clamped = max(0.1, days_until_deadline)
        deadline_urgency = max(1.0, round(10.0 / math.sqrt(days_clamped), 2))

        # 2. Goal Importance Score (Clamped 1.0 to 10.0)
        importance_score = max(1.0, min(10.0, goal_importance))

        # 3. Dependency Impact Score
        dependency_impact = downstream_dependencies_count * 2.0

        # 4. User Preference Weight
        pref_score = max(0.5, min(3.0, user_preference_weight))

        total_score = round(deadline_urgency + importance_score + dependency_impact + pref_score, 2)

        if total_score >= 15.0:
            priority_label = "HIGH"
        elif total_score >= 8.0:
            priority_label = "MEDIUM"
        else:
            priority_label = "LOW"

        return {
            "total_score": total_score,
            "priority_label": priority_label,
            "deadline_urgency": deadline_urgency,
            "goal_importance": importance_score,
            "dependency_impact": dependency_impact,
            "user_preference": pref_score,
        }
