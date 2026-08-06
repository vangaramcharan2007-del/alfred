"""Dynamic Replanner for Jarvis X (Layer 2 - Planning).

Adjusts execution targets based on reality (e.g. user studied 30 mins daily instead of 3 hours).
Dynamically reduces targets to achievable consistency levels and updates goal plans.
"""

from typing import Any, Dict, List, Optional

from jarvisx.goals import GoalTracker


class Replanner:
    """Zero-fluff production dynamic replanning engine."""

    def __init__(self, goal_tracker: Optional[GoalTracker] = None):
        self.goal_tracker = goal_tracker or GoalTracker()

    def dynamically_adjust_plan(
        self,
        goal_id: str,
        target_hours_per_day: float = 3.0,
        actual_hours_per_day: float = 0.5,
    ) -> Dict[str, Any]:
        """Adjust daily plan targets when actual performance deviates from target."""
        ratio = actual_hours_per_day / max(0.1, target_hours_per_day)

        if ratio < 0.5:
            # Scale down to sustainable micro-target (e.g. 45 mins) to build consistency
            adjusted_target = max(0.75, round(actual_hours_per_day * 1.5, 2))
            new_action = f"Focus on {int(adjusted_target*60)}-minute daily consistency sessions"
            reason = f"Actual study pace ({actual_hours_per_day:.1f}h/day) fell below target ({target_hours_per_day:.1f}h/day)."
        else:
            adjusted_target = target_hours_per_day
            new_action = "Maintain current momentum"
            reason = "Study pace aligns with target expectations."

        # Update goal progress and next action in GoalTracker
        res = self.goal_tracker.update_goal_progress(
            goal_id=goal_id,
            progress=min(0.99, max(0.1, ratio)),
            status="IN_PROGRESS",
            next_action=new_action,
        )

        return {
            "status": "REPLANNED",
            "goal_id": goal_id,
            "original_target_hours": target_hours_per_day,
            "actual_hours": actual_hours_per_day,
            "adjusted_target_hours": adjusted_target,
            "new_next_action": new_action,
            "reason": reason,
            "updated_goal": res,
        }
