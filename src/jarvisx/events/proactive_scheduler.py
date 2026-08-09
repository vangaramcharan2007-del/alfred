"""Proactive Background Scheduler for Phase 104.3."""

from __future__ import annotations
import logging
import threading
import time
from typing import Any, Dict, List, Optional
from jarvisx.events.event_bus import EventBus
from jarvisx.events.models import EventType, SystemEvent

logger = logging.getLogger("jarvisx.scheduler")


class ProactiveScheduler:
    """Runs ambient background timers to evaluate deadlines, habit streaks, memory decay, and morning briefings."""

    def __init__(
        self,
        event_bus: EventBus,
        check_interval_seconds: float = 60.0,
    ):
        self.event_bus = event_bus
        self.interval = check_interval_seconds
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.last_decay_run = 0.0
        self.last_deadline_check = 0.0
        self.last_habit_check = 0.0

    def start(self):
        """Start the background scheduler thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._scheduler_loop, name="ProactiveSchedulerThread", daemon=True)
        self._thread.start()
        logger.info("Proactive Scheduler started.")

    def stop(self):
        """Stop the background scheduler."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _scheduler_loop(self):
        while self._running:
            now = time.time()

            # 1. Daily Memory Decay Cycle (every 24h or manual)
            if now - self.last_decay_run > 86400.0:
                self.trigger_decay_cycle()
                self.last_decay_run = now

            # 2. Hourly Deadline & Syllabus Check (every 1h)
            if now - self.last_deadline_check > 3600.0:
                self.check_deadlines()
                self.last_deadline_check = now

            # 3. Habit & Streak Check (every 6h)
            if now - self.last_habit_check > 21600.0:
                self.check_habits()
                self.last_habit_check = now

            # Sleep in small increments
            for _ in range(int(self.interval * 2)):
                if not self._running:
                    break
                time.sleep(0.5)

    def trigger_decay_cycle(self) -> str:
        """Publish MEMORY_DECAY_CYCLE event."""
        event = SystemEvent(
            event_type=EventType.MEMORY_DECAY_CYCLE,
            priority=4,
            origin="ProactiveScheduler",
            payload={"action": "prune_decayed_memories"},
        )
        return self.event_bus.publish(event)

    def check_deadlines(self) -> str:
        """Publish DEADLINE_APPROACHING scan event."""
        event = SystemEvent(
            event_type=EventType.DEADLINE_APPROACHING,
            priority=7,
            origin="ProactiveScheduler",
            payload={"scan": "academic_calendar", "target_cgpa": "10.0"},
        )
        return self.event_bus.publish(event)

    def check_habits(self) -> str:
        """Publish HABIT_MISSED scan event."""
        event = SystemEvent(
            event_type=EventType.HABIT_MISSED,
            priority=6,
            origin="ProactiveScheduler",
            payload={"habit": "DSA Practice", "threshold_days": 1},
        )
        return self.event_bus.publish(event)

    def synthesize_morning_briefing(self, profile_summary: Optional[str] = None) -> str:
        """Synthesize proactive daily morning briefing."""
        date_str = time.strftime("%A, %B %d, %Y")
        lines = [
            f"=== [JARVIS X MORNING BRIEFING - {date_str}] ===",
            "Good morning! Here is your autonomous daily intelligence overview:",
            "",
            "[*] [ACADEMIC & ENGINEERING FOCUS]",
            f"  - Profile: {profile_summary or 'Targeting 10 CGPA in BTech CSE BDA & Master DSA'}",
            "  - Primary Goal: 10 CGPA Target | DSA LeetCode Mastery",
            "",
            "[*] [UPCOMING MILESTONES & DEADLINES]",
            "  - Midterm Semester Exams : Approaching in ~14 days",
            "  - DBMS Normalization Lab : Due Friday",
            "  - Computer Networks Lab  : Queue Assignment ready",
            "",
            "[*] [RECOMMENDED AUTONOMOUS MISSIONS]",
            "  1. [DSA] Solve 2 Graph / Dynamic Programming problems",
            "  2. [DBMS] Complete Normalization Form revision notes in Obsidian",
            "  3. [Jarvis X] Verify Phase 104 Daemon presence and IPC latency",
            "",
            "Stand by for instructions. Have a productive day!",
            "==================================================",
        ]
        return "\n".join(lines)
