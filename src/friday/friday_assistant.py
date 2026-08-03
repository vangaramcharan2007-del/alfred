from __future__ import annotations
import sys
import time
from typing import Dict, Any, List, Optional

from friday.persistence import FridayPersistenceManager
from friday.schedule_manager import FridayScheduleManager
from friday.cgpa_planner import FridayCGPAPlanner
from friday.assignment_tracker import FridayAssignmentTracker
from friday.health_reminders import FridayHealthReminders
from friday.habit_tracker import FridayHabitTracker
from friday.notes_goals import FridayNotesAndGoals

class FridayAssistant:
    """
    Friday Personal AI Assistant Controller.
    Manages daily schedule, 10 CGPA planning, assignments, health, habits, and voice/chat interaction.
    """
    def __init__(self):
        self.persistence = FridayPersistenceManager()
        self.schedule_mgr = FridayScheduleManager(self.persistence)
        self.cgpa_planner = FridayCGPAPlanner(self.persistence)
        self.assignment_tracker = FridayAssignmentTracker(self.persistence)
        self.health_reminders = FridayHealthReminders()
        self.habit_tracker = FridayHabitTracker(self.persistence)
        self.notes_goals = FridayNotesAndGoals(self.persistence)

    def print_daily_dashboard(self):
        schedule = self.schedule_mgr.get_todays_schedule()
        cgpa_plan = self.cgpa_planner.get_plan()
        assignments = self.assignment_tracker.get_pending_assignments()
        health = self.health_reminders.get_health_status()
        habits = self.habit_tracker.get_habits()
        goals = self.notes_goals.get_notes_and_goals()

    def generate_proactive_alerts(self) -> List[str]:
        alerts = []
        assignments = self.assignment_tracker.get_pending_assignments()
        for a in assignments:
            if "Tomorrow" in a.get("due_date", "") or "IN_PROGRESS" in a.get("status", ""):
                alerts.append(f"Assignment Alert: '{a['title']}' ({a['subject']}) is due {a['due_date'].lower()}!")

        schedule = self.schedule_mgr.get_todays_schedule()
        if schedule:
            dsa_slot = next((s for s in schedule if "algorithm" in s['activity'].lower() or "dsa" in s['activity'].lower()), None)
            if dsa_slot:
                alerts.append(f"Study Alert: You scheduled '{dsa_slot['activity']}' for [{dsa_slot['time_slot']}]. Ready to start?")

        alerts.append("Hydration Alert: You have completed 2.5L / 3.0L today -- drink 1 glass of water now.")
        alerts.append("JarvisX Milestone: You have 14 consecutive days of daily system programming commitments!")
        return alerts

    def print_daily_dashboard(self):
        schedule = self.schedule_mgr.get_todays_schedule()
        cgpa_plan = self.cgpa_planner.get_plan()
        assignments = self.assignment_tracker.get_pending_assignments()
        health = self.health_reminders.get_health_status()
        habits = self.habit_tracker.get_habits()
        goals = self.notes_goals.get_notes_and_goals()
        alerts = self.generate_proactive_alerts()

        print("==============================================")
        print("               FRIDAY AI ASSISTANT")
        print("==============================================")
        print("  \"Hello Ramcharan! Here is your daily overview.\"\n")

        print("[PROACTIVE ALERTS] Executive Reminders:")
        for alert in alerts:
            print(f"  ! {alert}")
        print()

        print("[ACADEMICS] 10 CGPA Target & Strategy:")
        print(f"  - Status          : {cgpa_plan['status']}")
        print(f"  - Projected CGPA  : {cgpa_plan['projected_cgpa']} / 10.0")
        print(f"  - Key Strategy    : {cgpa_plan['strategy']}\n")

        print("[SCHEDULE] Today's Timetable & Classes:")
        for s in schedule:
            print(f"  - [{s['time_slot']}] {s['activity']}")
        print()

        print("[ASSIGNMENTS] Pending Academic Work:")
        for a in assignments:
            print(f"  - {a['title']} ({a['subject']}) -- Due: {a['due_date']} [{a['status']}]")
        print()

        print("[HABITS] Daily Consistency & Streaks:")
        for h in habits:
            print(f"  - {h['habit_name']}: {h['streak_count']} day streak! ({h['last_completed']})")
        print()

        print("[HEALTH & FOCUS] Fitness, Hydration & Pomodoro:")
        print(f"  - Hydration       : {health['hydration_recommendation']}")
        print(f"  - Pomodoro        : {health['pomodoro_recommendation']}")
        print(f"  - Fitness         : {health['fitness_reminder']}\n")

        print("[GOALS & NOTES] Academic & Personal Growth:")
        for g in goals:
            print(f"  - [{g['type'].upper()}] {g['content']}")
        print("==============================================\n")



    def run_interactive_shell(self):
        self.print_daily_dashboard()
