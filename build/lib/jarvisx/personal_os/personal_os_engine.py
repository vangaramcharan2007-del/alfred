"""Master Personal OS & Life Context Engine for Phase 94."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.personal_os.models import Goal, DailyPriority, TopicMastery
from jarvisx.personal_os.life_memory import LifeMemory
from jarvisx.personal_os.goal_manager import GoalManager
from jarvisx.personal_os.syllabus_tracker import SyllabusTracker
from jarvisx.personal_os.habit_tracker import HabitTracker
from jarvisx.personal_os.priority_engine import PriorityEngine


class PersonalOSEngine:
    """Master Personal OS Coordinator for Jarvis X.
    Connects human long-term life objectives directly into the Mission Runtime.
    """

    def __init__(self):
        self.memory = LifeMemory()
        self.goals = GoalManager(self.memory)
        self.syllabus = SyllabusTracker(self.memory)
        self.habits = HabitTracker(self.memory)
        self.priorities = PriorityEngine(self.goals, self.syllabus, self.habits, self.memory)

    def show_goals(self) -> List[Goal]:
        goals = self.goals.list_goals()
        avg_mastery = self.syllabus.get_subject_average_mastery()
        for g in goals:
            self.goals.evaluate_goal_risk(g.id, avg_mastery)

        print(f"\n[PERSONAL OS]: Long-Term Life Goals ({len(goals)} active)")
        for g in goals:
            risk_flag = f" [!] {g.status.value}" if g.status.value != "ACTIVE" else " [OK]"
            print(f"  • {g.title} ({g.progress_pct}% complete){risk_flag}")
            if g.risk_reason:
                print(f"    Reason: {g.risk_reason}")
            for m in g.milestones:
                chk = "[X]" if m.completed else "[ ]"
                print(f"      {chk} {m.title} (Deadline: {m.deadline})")
        return goals

    def show_syllabus(self) -> Dict[str, Any]:
        topics = self.syllabus.memory.list_topics()
        weak = self.syllabus.get_weak_areas()
        print(f"\n[ACADEMIC SYLLABUS]: Curriculum & Topic Mastery ({len(topics)} topics)")
        for t in topics:
            flag = " [WEAK]" if t.mastery_score < 50.0 else " [MASTERED]"
            print(f"  • {t.subject} -> {t.topic}: {int(t.mastery_score)}% mastery{flag}")
            for ev in t.evidence:
                print(f"      - Evidence ({ev.type}): {ev.description}")
        return {"total_topics": len(topics), "weak_topics": len(weak), "topics": [t.to_dict() for t in topics]}

    def show_habits(self) -> Dict[str, Any]:
        summary = self.habits.get_habit_summary()
        print(f"\n[BEHAVIOR & HABIT TRACKER]:")
        print(f"  • Average Daily Focus: {summary['average_daily_hours']}h (Streak: {summary['current_streak_days']} days)")
        for p in summary["patterns_detected"]:
            print(f"  • Pattern Detected: {p}")
        return summary

    def show_priorities(self) -> List[DailyPriority]:
        prios = self.priorities.calculate_daily_priorities()
        print(f"\n[DAILY ENGINEERING & STUDY PRIORITIES]: Top {len(prios)} Actions")
        for idx, p in enumerate(prios, 1):
            print(f"  {idx}. {p.task} (Score: {p.score}/100)")
            print(f"     Explanation: {p.explanation}")
            print(f"     Breakdown: Weakness={p.breakdown['weakness']}, Urgency={p.breakdown['deadline_urgency']}, Goal={p.breakdown['goal_importance']}, Habit={p.breakdown['habit_inconsistency']}")
        return prios

    def dispatch_top_priority_mission(self) -> Dict[str, Any]:
        """Handshake: Takes the #1 calculated priority and dispatches it directly to the Mission Runtime!"""
        prios = self.show_priorities()
        if not prios:
            return {"status": "NO_PRIORITIES", "message": "All goals on track."}

        top = prios[0]
        print(f"\n[Personal OS -> Mission Runtime Handshake]:")
        print(f"  Dispatching Mission: '{top.generated_mission_goal}'")

        from jarvisx.agents.agent_executor import AutonomousAgentExecutor
        executor = AutonomousAgentExecutor()
        mission_res = executor.execute_mission(top.generated_mission_goal)

        return {
            "status": "DISPATCHED_AND_COMPLETED",
            "priority_task": top.task,
            "priority_score": top.score,
            "mission_goal": top.generated_mission_goal,
            "mission_result": mission_res,
        }
