"""Context Monitor (The Eyes of Proactive Intelligence) for Phase 95."""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.personal_os.life_memory import LifeMemory
from jarvisx.personal_os.syllabus_tracker import SyllabusTracker
from jarvisx.personal_os.habit_tracker import HabitTracker
from jarvisx.proactive.models import RiskSignal, SignalType
from jarvisx.proactive.proactive_memory import ProactiveMemory


class ContextMonitor:
    """Continuously observes syllabus, calendar deadlines, and habit drift to detect risk signals."""

    def __init__(
        self,
        life_mem: Optional[LifeMemory] = None,
        proactive_mem: Optional[ProactiveMemory] = None,
    ):
        self.life_mem = life_mem or LifeMemory()
        self.proactive_mem = proactive_mem or ProactiveMemory()
        self.syllabus = SyllabusTracker(self.life_mem)
        self.habits = HabitTracker(self.life_mem)

    def scan_for_risks(self, vacation_override: bool = False) -> List[RiskSignal]:
        """Scan curriculum and study habits, generating structured RiskSignals with confidence ratings."""
        signals: List[RiskSignal] = []
        now = time.time()

        # 1. Scan Academic Weak Areas & Exam Proximity
        weak_topics = self.syllabus.get_weak_areas()
        for t in weak_topics:
            if t.mastery_score < 50.0:
                severity = 100.0 - t.mastery_score
                # High confidence if verified by low quiz score or long lapse
                conf = 0.92 if len(t.evidence) >= 2 else 0.70
                reasons = [f"Mastery score is {int(t.mastery_score)}% (<50% threshold)"]
                for ev in t.evidence:
                    reasons.append(f"{ev.type}: {ev.description}")

                sig = RiskSignal(
                    id=f"risk_{t.subject}_{t.topic}".lower().replace(" ", "_"),
                    type=SignalType.ACADEMIC_RISK,
                    source=f"{t.subject}: {t.topic}",
                    severity=round(severity, 1),
                    confidence=conf,
                    reason=reasons,
                    timestamp=now,
                    is_suppressed=vacation_override,
                )
                self.proactive_mem.save_risk_signal(sig)
                signals.append(sig)

        # 2. Scan Habit Inconsistency & Drift
        habit_sum = self.habits.get_habit_summary()
        if habit_sum["average_daily_hours"] < 1.5:
            sig_habit = RiskSignal(
                id="risk_habit_drift",
                type=SignalType.HABIT_DRIFT,
                source="Study Routine",
                severity=65.0,
                confidence=0.85,
                reason=[f"Average daily study hours dropped to {habit_sum['average_daily_hours']}h"],
                timestamp=now,
                is_suppressed=vacation_override,
            )
            self.proactive_mem.save_risk_signal(sig_habit)
            signals.append(sig_habit)

        return signals
