"""Progress Intelligence Engine for Jarvis X (Layer 2 - Planning).

Analyzes mission completion rates, time spent, approaching deadlines, and user performance
to detect risks like falling_behind, unrealistic_plans, and blocked_dependencies.
"""

from typing import Any, Dict, List, Optional

from jarvisx.goals import GoalTracker


class ProgressIntelligence:
    """Zero-fluff production progress intelligence engine."""

    def __init__(self, goal_tracker: Optional[GoalTracker] = None):
        self.goal_tracker = goal_tracker or GoalTracker()

    def analyze_execution_progress(self, execution_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze execution history and detect risks."""
        active_goals = self.goal_tracker.get_active_goals()
        completed_count = sum(1 for e in execution_history if e.get("outcome") in ("completed", "nominal", "SUCCESS"))
        failed_count = sum(1 for e in execution_history if e.get("outcome") in ("failed", "error", "FAILED"))
        total_missions = len(execution_history)

        completion_rate = completed_count / max(1, total_missions)

        detected_risks = []

        # Risk 1: Falling Behind Check
        for g in active_goals:
            prog = g.get("progress", 0.0)
            deadline = g.get("deadline", "")
            if prog < 0.5 and deadline != "Not specified":
                detected_risks.append({
                    "risk_type": "FALLING_BEHIND",
                    "goal": g.get("goal"),
                    "details": f"Goal '{g.get('goal')}' is at {int(prog*100)}% progress with deadline '{deadline}'.",
                })

        # Risk 2: Unrealistic Plans Check (High failure rate or low completion rate)
        if failed_count > 0 and completion_rate < 0.60:
            detected_risks.append({
                "risk_type": "UNREALISTIC_PLANS",
                "details": f"Completion rate is {int(completion_rate*100)}% ({failed_count} failed executions). Targets may exceed daily capacity.",
            })

        # Risk 3: Blocked Dependencies Check
        for g in active_goals:
            if g.get("status") == "BLOCKED":
                detected_risks.append({
                    "risk_type": "BLOCKED_DEPENDENCIES",
                    "goal": g.get("goal"),
                    "details": f"Goal '{g.get('goal')}' is BLOCKED waiting on prerequisite tasks.",
                })

        return {
            "status": "completed",
            "total_missions_analyzed": total_missions,
            "completed_count": completed_count,
            "failed_count": failed_count,
            "completion_rate": round(completion_rate, 2),
            "risks_detected": detected_risks,
            "has_risks": len(detected_risks) > 0,
        }
