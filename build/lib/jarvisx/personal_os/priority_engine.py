"""Transparent & Explainable Daily Priority Engine for Phase 94 Personal OS Layer."""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.personal_os.models import DailyPriority
from jarvisx.personal_os.goal_manager import GoalManager
from jarvisx.personal_os.syllabus_tracker import SyllabusTracker
from jarvisx.personal_os.habit_tracker import HabitTracker
from jarvisx.personal_os.life_memory import LifeMemory


class PriorityEngine:
    """Computes daily high-impact action priorities using transparent weighted scoring."""

    def __init__(
        self,
        goals: Optional[GoalManager] = None,
        syllabus: Optional[SyllabusTracker] = None,
        habits: Optional[HabitTracker] = None,
        memory: Optional[LifeMemory] = None,
    ):
        self.memory = memory or LifeMemory()
        self.goals = goals or GoalManager(self.memory)
        self.syllabus = syllabus or SyllabusTracker(self.memory)
        self.habits = habits or HabitTracker(self.memory)

    def calculate_daily_priorities(self, date_str: Optional[str] = None) -> List[DailyPriority]:
        """Compute top 3 explainable priorities based on:
        Priority Score = 0.35 * Weakness + 0.30 * DeadlineUrgency + 0.20 * GoalImportance + 0.15 * HabitInconsistency
        """
        d = date_str or time.strftime("%Y-%m-%d")
        weak_topics = self.syllabus.get_weak_areas()
        active_goals = self.goals.list_goals()
        habits_summary = self.habits.get_habit_summary()

        priorities: List[DailyPriority] = []

        for topic in weak_topics:
            # Component 1: Weakness (100 - mastery_score)
            weakness_score = 100.0 - topic.mastery_score

            # Component 2: Deadline Urgency (Simulated proximity: 80/100)
            deadline_urgency = 85.0 if topic.last_revision_days_ago > 7 else 60.0

            # Component 3: Goal Importance (10 CGPA = 95.0)
            goal_importance = 95.0 if any(g.category == "academic" for g in active_goals) else 70.0

            # Component 4: Habit Inconsistency (If recent study hours < 1.0)
            habit_inconsistency = 75.0 if habits_summary.get("average_daily_hours", 0) < 2.0 else 40.0

            # Weighted Aggregate Score
            score = round(
                (0.35 * weakness_score) +
                (0.30 * deadline_urgency) +
                (0.20 * goal_importance) +
                (0.15 * habit_inconsistency),
                2
            )

            breakdown = {
                "weakness": round(0.35 * weakness_score, 2),
                "deadline_urgency": round(0.30 * deadline_urgency, 2),
                "goal_importance": round(0.20 * goal_importance, 2),
                "habit_inconsistency": round(0.15 * habit_inconsistency, 2),
                "raw_weakness_pct": round(weakness_score, 1),
                "mastery_score": topic.mastery_score,
            }

            explanation = (
                f"Selected {topic.subject} ({topic.topic}) because mastery is {int(topic.mastery_score)}% (weakness), "
                f"last revised {topic.last_revision_days_ago} days ago (deadline urgency), "
                f"and it directly impacts your 10 CGPA academic goal."
            )

            mission_goal = f"Prepare crash revision notes and practice quiz for {topic.subject}: {topic.topic}"

            priorities.append(DailyPriority(
                task=f"Revise {topic.subject}: {topic.topic}",
                score=score,
                breakdown=breakdown,
                explanation=explanation,
                generated_mission_goal=mission_goal,
            ))

        priorities.sort(key=lambda p: p.score, reverse=True)
        top_priorities = priorities[:3]

        self.memory.save_daily_priorities(top_priorities, d)
        return top_priorities
