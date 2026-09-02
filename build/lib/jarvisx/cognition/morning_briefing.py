"""
Morning Autonomous Briefing Generator.
Unifies Academics (classes, top subject, assignments), Engineering (git status, failing tests, next action),
and Life habits into a single morning briefing with workspace prep prompt.
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from friday.academic_war_mode import AcademicWarMode
from jarvisx.cognition.daily_engineering import DailyEngineeringContext
from friday.persistence import FridayPersistenceManager


class MorningBriefingGenerator:
    """
    Generates unified morning briefing for Ramcharan.
    """

    def generate_briefing(self, cwd: str = ".") -> Dict[str, Any]:
        hour = float(os.environ.get("MOCK_HOUR", 8.0))
        if hour < 12:
            time_greeting = "Good morning Ramcharan."
        elif hour < 17:
            time_greeting = "Good afternoon Ramcharan."
        else:
            time_greeting = "Good evening Ramcharan."

        # 1. Academic status
        awm = AcademicWarMode()
        war_strat = awm.get_war_strategy()
        pm = FridayPersistenceManager()
        schedule = pm.get_schedule()
        assignments = pm.get_assignments()

        first_class = schedule[0]["activity"] if schedule else "No classes scheduled"

        # 2. Engineering status
        dec = DailyEngineeringContext()
        eng_ctx = dec.generate_briefing(cwd)

        # 3. Life status
        habits = pm.get_habits()
        habit_str = ", ".join([f"{h['habit_name']} ({h['streak_count']}d streak)" for h in habits[:2]])

        briefing_text = (
            f"{time_greeting}\n\n"
            f"[ACADEMICS]\n"
            f"  - First Class: {first_class}\n"
            f"  - High Impact Focus: {war_strat['daily_recommendation']}\n"
            f"  - Pending Assignments: {len(assignments)} pending\n\n"
            f"[ENGINEERING]\n"
            f"  - Git Status: {eng_ctx['modified_count']} modified files on '{eng_ctx['branch']}'\n"
            f"  - Sandbox Status: {eng_ctx['test_status']}\n"
            f"  - Recommended Action: {eng_ctx['recommended_action']}\n\n"
            f"[LIFE & HABITS]\n"
            f"  - Streaks: {habit_str}\n\n"
            f"Would you like me to prepare your workspace?"
        )

        return {
            "status": "SUCCESS",
            "greeting": time_greeting,
            "first_class": first_class,
            "top_academic_subject": war_strat["top_focus"]["subject"] if war_strat.get("top_focus") else "N/A",
            "modified_files": eng_ctx["modified_count"],
            "test_status": eng_ctx["test_status"],
            "briefing_text": briefing_text
        }
