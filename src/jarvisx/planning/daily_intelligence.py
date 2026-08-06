"""Alfred Daily Executive Intelligence Briefing (Layer 2 - Planning).

Synthesizes daily priorities, risk warnings, and recommended focus missions.
"""

from typing import Any, Dict, List, Optional

from jarvisx.goals import GoalTracker
from jarvisx.planning.progress_intelligence import ProgressIntelligence
from jarvisx.planning.prioritizer import Prioritizer


class DailyIntelligenceBriefing:
    """Zero-fluff production daily intelligence briefing engine."""

    def __init__(
        self,
        goal_tracker: Optional[GoalTracker] = None,
        progress_intel: Optional[ProgressIntelligence] = None,
    ):
        self.goal_tracker = goal_tracker or GoalTracker()
        self.progress_intel = progress_intel or ProgressIntelligence(goal_tracker=self.goal_tracker)
        self.prioritizer = Prioritizer()

    def generate_daily_report(self, execution_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Synthesize daily intelligence report with priorities, risks, and recommended missions."""
        active_goals = self.goal_tracker.get_active_goals()
        history = execution_history or []
        prog_res = self.progress_intel.analyze_execution_progress(history)

        priorities = []
        for idx, g in enumerate(active_goals[:3]):
            priorities.append(f"{idx + 1}. {g.get('goal')} (Next: {g.get('next_action')})")

        if not priorities:
            priorities = [
                "1. Calculus assignment revision",
                "2. DSA algorithm practice",
                "3. Project feature engineering",
            ]

        risk_msg = "Zero active preparation risks detected."
        if prog_res["risks_detected"]:
            r = prog_res["risks_detected"][0]
            risk_msg = f"{r['risk_type']}: {r['details']}"

        rec_mission = "45-minute graph algorithms & linear algebra focus session."
        if active_goals:
            top = active_goals[0]
            rec_mission = f"45-minute focus session on '{top.get('goal')}'."

        report_lines = [
            "================================================",
            "                GOOD MORNING                    ",
            "================================================",
            "Today's priorities:",
            *[f"  {p}" for p in priorities],
            "",
            "Risk Analysis:",
            f"  [!] {risk_msg}",
            "",
            "Recommended mission:",
            f"  -> {rec_mission}",
            "================================================",
        ]

        return {
            "status": "completed",
            "priorities": priorities,
            "risk_analysis": risk_msg,
            "recommended_mission": rec_mission,
            "output": "\n".join(report_lines),
        }
