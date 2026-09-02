"""Life Events Engine for Phase 94.1 & Phase 95 Event-Driven Transitions."""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.personal_os.life_memory import LifeMemory
from jarvisx.proactive.proactive_memory import ProactiveMemory


class LifeEventEngine:
    """Emits life state transition events and recalculates urgency metrics."""

    def __init__(self, life_mem: Optional[LifeMemory] = None, proactive_mem: Optional[ProactiveMemory] = None):
        self.life_mem = life_mem or LifeMemory()
        self.proactive_mem = proactive_mem or ProactiveMemory()

    def emit_exam_date_changed(self, subject: str, old_date: str, new_date: str) -> Dict[str, Any]:
        """Recalculates urgency when exam timetable changes."""
        payload = {
            "subject": subject,
            "old_date": old_date,
            "new_date": new_date,
            "urgency_delta": +20.0,
            "emitted_at": time.time(),
        }
        self.proactive_mem.save_event(f"exam_{subject}_{int(time.time())}", "EXAM_DATE_CHANGED", payload)
        return payload

    def emit_habit_streak_broken(self, habit: str, missed_days: int) -> Dict[str, Any]:
        """Emits alert when user study streak lapses."""
        payload = {
            "habit": habit,
            "missed_days": missed_days,
            "action_needed": "SUGGEST_RECOVERY",
            "emitted_at": time.time(),
        }
        self.proactive_mem.save_event(f"streak_{habit}_{int(time.time())}", "HABIT_STREAK_BROKEN", payload)
        return payload

    def emit_vacation_override(self, reason: str = "Traveling / Vacation") -> Dict[str, Any]:
        """Suppresses false-positive alerts when user is on intentional leave."""
        payload = {"vacation_active": True, "reason": reason, "emitted_at": time.time()}
        self.proactive_mem.save_event(f"vacation_{int(time.time())}", "VACATION_OVERRIDE", payload)
        return payload
