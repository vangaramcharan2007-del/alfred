from __future__ import annotations
import sys
from datetime import date
from typing import Dict, Any, List

from friday.persistence import FridayPersistenceManager
from friday.schedule_manager import FridayScheduleManager
from friday.cgpa_planner import FridayCGPAPlanner
from friday.assignment_tracker import FridayAssignmentTracker
from friday.health_reminders import FridayHealthReminders
from friday.habit_tracker import FridayHabitTracker
from friday.notes_goals import FridayNotesAndGoals


class FridayAssistant:
    """
    Friday - Personal Executive AI Assistant.
    Manages academics, life organization, proactive reminders,
    time savings tracking, and knowledge base.
    """

    def __init__(self):
        self.persistence = FridayPersistenceManager()
        self.schedule_mgr = FridayScheduleManager(self.persistence)
        self.cgpa_planner = FridayCGPAPlanner(self.persistence)
        self.assignment_tracker = FridayAssignmentTracker(self.persistence)
        self.health_reminders = FridayHealthReminders()
        self.habit_tracker = FridayHabitTracker(self.persistence)
        self.notes_goals = FridayNotesAndGoals(self.persistence)

    # ------------------------------------------------------------------
    # Proactive alerts - only show what matters RIGHT NOW
    # ------------------------------------------------------------------
    def generate_proactive_alerts(self) -> List[str]:
        alerts = []

        # Urgent assignments
        for a in self.assignment_tracker.get_pending_assignments():
            due = a.get("due_date", "")
            if "Tomorrow" in due:
                alerts.append(f"URGENT: '{a['title']}' is due TOMORROW. Finish it tonight.")
            elif "IN_PROGRESS" in a.get("status", ""):
                alerts.append(f"'{a['title']}' is in progress -- keep pushing.")

        # Study time check
        studied = self.persistence.get_study_minutes_today()
        if studied < 60:
            alerts.append(f"You studied only {studied} min today. Target: 120 min. Start now.")
        elif studied < 120:
            alerts.append(f"Study progress: {studied}/120 min. {120 - studied} min remaining.")

        # Attendance warnings
        for c in self.persistence.get_cgpa_plan():
            att = c.get("attendance_pct", 100)
            if att < 75:
                alerts.append(f"ATTENDANCE DANGER: {c['subject']} at {att}%. Minimum 75% required.")
            elif att < 80:
                alerts.append(f"Attendance warning: {c['subject']} at {att}%. Avoid skipping.")

        # Syllabus behind
        for c in self.persistence.get_cgpa_plan():
            syl = c.get("syllabus_pct", 0)
            if syl < 60:
                alerts.append(f"Syllabus behind: {c['subject']} at {syl}% covered. Schedule extra revision.")

        return alerts

    # ------------------------------------------------------------------
    # Exam readiness estimator
    # ------------------------------------------------------------------
    def get_exam_readiness(self) -> List[Dict[str, Any]]:
        results = []
        for c in self.persistence.get_cgpa_plan():
            score = c.get("current_score", 0)
            syllabus = c.get("syllabus_pct", 0)
            att = c.get("attendance_pct", 100)
            # Weighted readiness: 40% score, 35% syllabus, 25% attendance
            readiness = round(score * 0.4 + syllabus * 0.35 + att * 0.25, 1)
            if readiness >= 85:
                verdict = "EXAM READY"
            elif readiness >= 70:
                verdict = "NEEDS REVISION"
            else:
                verdict = "AT RISK"
            results.append({
                "subject": c["subject"],
                "score": score,
                "syllabus_pct": syllabus,
                "attendance_pct": att,
                "readiness": readiness,
                "verdict": verdict,
            })
        return results

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def print_daily_dashboard(self):
        schedule = self.schedule_mgr.get_todays_schedule()
        cgpa_plan = self.cgpa_planner.get_plan()
        assignments = self.assignment_tracker.get_pending_assignments()
        health = self.health_reminders.get_health_status()
        habits = self.habit_tracker.get_habits()
        goals = self.notes_goals.get_notes_and_goals()
        alerts = self.generate_proactive_alerts()
        readiness = self.get_exam_readiness()
        study_today = self.persistence.get_study_minutes_today()
        saved_today = self.persistence.get_time_savings_today()
        saved_week = self.persistence.get_time_savings_week()
        saved_semester = self.persistence.get_time_savings_semester()

        print("==============================================")
        print("         FRIDAY - Executive Assistant")
        print(f"         {date.today().strftime('%A, %B %d, %Y')}")
        print("==============================================\n")

        # Proactive alerts (only if there are any)
        if alerts:
            print("[!] PROACTIVE ALERTS:")
            for alert in alerts:
                print(f"  ! {alert}")
            print()

        # Time savings
        print(f"[TIME SAVED] Today: {saved_today:.0f} min | This week: {saved_week:.0f} min | Semester: {saved_semester:.0f} min\n")

        # CGPA
        print(f"[CGPA] Projected: {cgpa_plan['projected_cgpa']} / 10.0 -- {cgpa_plan['status']}")
        print(f"  Strategy: {cgpa_plan['strategy']}\n")

        # Exam readiness
        print("[EXAM READINESS]")
        for r in readiness:
            print(f"  {r['subject']:<40} Score:{r['score']:>5.0f}%  Syllabus:{r['syllabus_pct']:>4.0f}%  Attendance:{r['attendance_pct']:>4.0f}%  --> {r['verdict']}")
        print()

        # Today's schedule
        print("[SCHEDULE]")
        for s in schedule:
            print(f"  [{s['time_slot']}] {s['activity']}")
        print()

        # Assignments
        print("[ASSIGNMENTS]")
        for a in assignments:
            marker = ">>>" if "Tomorrow" in a.get("due_date", "") else "   "
            print(f"  {marker} {a['title']} ({a['subject']}) -- Due: {a['due_date']} [{a['status']}]")
        print()

        # Study progress
        print(f"[STUDY] Today: {study_today} / 120 min")
        bar_filled = min(20, int(study_today / 120 * 20))
        print(f"  [{'#' * bar_filled}{'.' * (20 - bar_filled)}]\n")

        # Habits
        print("[HABITS]")
        for h in habits:
            print(f"  {h['habit_name']}: {h['streak_count']} day streak")
        print()

        # Health
        print("[HEALTH]")
        print(f"  Hydration : {health['hydration_recommendation']}")
        print(f"  Pomodoro  : {health['pomodoro_recommendation']}")
        print(f"  Fitness   : {health['fitness_reminder']}\n")

        # Goals
        print("[GOALS]")
        for g in goals:
            print(f"  [{g['type'].upper()}] {g['content']}")
        print("==============================================\n")

    def run_interactive_shell(self):
        self.print_daily_dashboard()
