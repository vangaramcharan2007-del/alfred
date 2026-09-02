"""Goal Manager for Phase 94 Personal OS Layer."""

from __future__ import annotations
import uuid
from typing import Dict, Any, List, Optional
from jarvisx.personal_os.models import Goal, GoalStatus, Milestone
from jarvisx.personal_os.life_memory import LifeMemory


class GoalManager:
    """Manages multi-week user objectives, milestone progress, and risk detection."""

    def __init__(self, memory: Optional[LifeMemory] = None):
        self.memory = memory or LifeMemory()
        self._ensure_default_goals()

    def _ensure_default_goals(self) -> None:
        if not self.memory.list_goals():
            default_goal = Goal(
                id="academic_10_cgpa",
                title="Achieve 10 CGPA Academic Mastery",
                category="academic",
                target_date="2026-11-30",
                progress_pct=45.0,
                status=GoalStatus.ACTIVE,
                milestones=[
                    Milestone("m1", "Master Unit 1-3 in Java & OOP", "2026-08-20", completed=True),
                    Milestone("m2", "Complete Operating Systems Concurrency Project", "2026-09-10", completed=False),
                    Milestone("m3", "Score 95%+ in Mid-Term Examinations", "2026-10-15", completed=False),
                ]
            )
            self.memory.save_goal(default_goal)

    def create_goal(self, title: str, category: str = "academic", target_date: str = "2026-12-31") -> Goal:
        goal_id = str(uuid.uuid4())[:8]
        goal = Goal(
            id=goal_id,
            title=title,
            category=category,
            target_date=target_date,
            progress_pct=0.0,
            status=GoalStatus.ACTIVE,
            milestones=[Milestone(f"{goal_id}_m1", f"Initial milestone for {title}", target_date, False)]
        )
        self.memory.save_goal(goal)
        return goal

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        return self.memory.get_goal(goal_id)

    def list_goals(self) -> List[Goal]:
        return self.memory.list_goals()

    def evaluate_goal_risk(self, goal_id: str, average_topic_mastery: float) -> Goal:
        """Evaluate if goal is AT_RISK due to low syllabus mastery or upcoming deadlines."""
        goal = self.memory.get_goal(goal_id)
        if not goal:
            raise ValueError(f"Goal '{goal_id}' not found.")

        if average_topic_mastery < 50.0:
            goal.status = GoalStatus.AT_RISK
            goal.risk_reason = f"Average syllabus mastery ({int(average_topic_mastery)}%) is below the 50% safety threshold."
        else:
            goal.status = GoalStatus.ACTIVE
            goal.risk_reason = None

        self.memory.save_goal(goal)
        return goal
