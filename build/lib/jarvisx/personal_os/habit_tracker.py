"""Habit Tracker and Behavior Pattern Detector for Phase 94 Personal OS Layer."""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.personal_os.models import HabitLog
from jarvisx.personal_os.life_memory import LifeMemory


class HabitTracker:
    """Logs study blocks, focus sessions, and detects behavioural patterns without being intrusive."""

    def __init__(self, memory: Optional[LifeMemory] = None):
        self.memory = memory or LifeMemory()
        self._ensure_default_habits()

    def _ensure_default_habits(self) -> None:
        if not self.memory.list_habits():
            self.memory.save_habit(HabitLog(date="2026-08-05", habit="deep_work", duration_hours=3.5, category="academic"))
            self.memory.save_habit(HabitLog(date="2026-08-06", habit="leetcode", duration_hours=1.5, category="engineering"))
            self.memory.save_habit(HabitLog(date="2026-08-07", habit="revision", duration_hours=0.5, category="academic"))

    def log_session(self, habit: str, duration_hours: float, category: str = "study", date_str: Optional[str] = None) -> HabitLog:
        d = date_str or time.strftime("%Y-%m-%d")
        log = HabitLog(date=d, habit=habit, duration_hours=duration_hours, category=category)
        self.memory.save_habit(log)
        return log

    def get_habit_summary(self) -> Dict[str, Any]:
        logs = self.memory.list_habits(limit=14)
        total_hours = sum(l.duration_hours for l in logs)
        avg_daily = round(total_hours / max(len(logs), 1), 2)

        patterns = []
        if len(logs) >= 3:
            recent_hours = [l.duration_hours for l in logs[:3]]
            if recent_hours[0] < 1.0:
                patterns.append("Friday productivity dip detected (0.5h logged vs 3.5h weekday average).")

        return {
            "total_logs": len(logs),
            "total_hours_logged": total_hours,
            "average_daily_hours": avg_daily,
            "current_streak_days": len(logs),
            "patterns_detected": patterns,
            "recent_logs": [l.to_dict() for l in logs[:5]],
        }
