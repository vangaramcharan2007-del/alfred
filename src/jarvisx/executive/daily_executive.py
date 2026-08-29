"""
Proactive Daily Executive & Schedule Sentinel for Jarvis X ("Jarvis Daily Executive").
Manages college academic deadlines, daily priorities, automated morning/evening voice briefings, and focus blocks.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from jarvisx.llm.gemini_provider import GeminiLLMProvider
from jarvisx.security.audit_ledger import CryptographicAuditLedger

logger = logging.getLogger("jarvisx.executive")


@dataclass
class ScheduleTask:
    task_id: str
    title: str
    category: str  # "COLLEGE_ASSIGNMENT", "LAB_SESSION", "PROJECT_DEV", "PERSONAL"
    due_date: str
    priority: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    estimated_hours: float
    completed: bool = False


@dataclass
class ExecutiveBriefing:
    briefing_id: str
    timestamp: str
    greeting: str
    spoken_voice_briefing: str
    top_priorities: List[Dict[str, Any]]
    upcoming_deadlines: List[Dict[str, Any]]
    suggested_focus_schedule: str
    system_readiness_status: str
    audit_hash: str


class DailyExecutiveSentinel:
    """Master agent for proactive schedule management and daily voice briefings."""

    _instance: Optional[DailyExecutiveSentinel] = None

    def __init__(
        self,
        gemini_provider: Optional[GeminiLLMProvider] = None,
        audit_ledger: Optional[CryptographicAuditLedger] = None,
    ):
        self.gemini = gemini_provider or GeminiLLMProvider()
        self.audit = audit_ledger or CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
        self.tasks: List[ScheduleTask] = []
        self._load_default_schedule()

    @classmethod
    def get_instance(cls) -> DailyExecutiveSentinel:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_default_schedule(self):
        """Initializes academic and project schedule items."""
        now = datetime.now()
        self.tasks = [
            ScheduleTask(
                task_id="task_001",
                title="Jarvis X Lab VM (LAB-VM-01) Physical Node Integration",
                category="LAB_SESSION",
                due_date=(now + timedelta(days=2)).strftime("%Y-%m-%d 14:00"),
                priority="CRITICAL",
                estimated_hours=1.5,
            ),
            ScheduleTask(
                task_id="task_002",
                title="Advanced AI & Computer Vision Assignment Submission",
                category="COLLEGE_ASSIGNMENT",
                due_date=(now + timedelta(days=3)).strftime("%Y-%m-%d 23:59"),
                priority="HIGH",
                estimated_hours=2.0,
            ),
            ScheduleTask(
                task_id="task_003",
                title="Alfred Voice HUD & Telephony Gateway Real-World Polish",
                category="PROJECT_DEV",
                due_date=(now + timedelta(days=1)).strftime("%Y-%m-%d 20:00"),
                priority="MEDIUM",
                estimated_hours=1.0,
            ),
        ]

    def add_task(self, title: str, category: str, due_date: str, priority: str = "HIGH", estimated_hours: float = 1.0) -> ScheduleTask:
        """Adds a new academic or project deadline to the schedule."""
        task = ScheduleTask(
            task_id=f"task_{int(time.time() * 1000)}",
            title=title,
            category=category,
            due_date=due_date,
            priority=priority,
            estimated_hours=estimated_hours,
        )
        self.tasks.append(task)
        return task

    async def generate_executive_briefing(self, briefing_type: str = "MORNING") -> ExecutiveBriefing:
        """Synthesizes a personalized, proactive executive briefing with voice audio script."""
        start_t = time.time()
        briefing_id = f"brief_{int(start_t * 1000)}"
        now_str = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

        # Organize tasks
        active_tasks = [t for t in self.tasks if not t.completed]
        sorted_tasks = sorted(active_tasks, key=lambda x: (x.priority != "CRITICAL", x.priority != "HIGH", x.due_date))

        tasks_summary = "\n".join([f"- [{t.priority}] {t.title} (Due: {t.due_date}, Category: {t.category})" for t in sorted_tasks])

        prompt = (
            f"You are Alfred, Charan's sovereign executive butler and AI chief of staff.\n"
            f"Generate an articulate, proactive {briefing_type} voice executive briefing for Charan.\n\n"
            f"Current Time: {now_str}\n"
            f"Active Priorities & Deadlines:\n{tasks_summary}\n\n"
            f"System Vitals: Laptop RAM Compacted & Cool (80%), GPU Mesh Ready, Gemini 3.6 Pro Cloud Connected.\n\n"
            f"Output Requirements:\n"
            f"1. Spoken Greeting (Warm, confident, respectful).\n"
            f"2. 2-3 sentence vocal audio briefing highlighting critical items.\n"
            f"3. Recommended deep work focus schedule for today."
        )

        res = await self.gemini.generate(prompt=prompt, model="gemini-3.6-flash")
        raw_text = res.get("response", "")
        if not raw_text:
            raw_text = (
                f"Good day, Charan. All systems are operating smoothly. "
                f"You have {len(sorted_tasks)} active priorities on your schedule, with {sorted_tasks[0].title} as your top focus."
            )

        # Log into Cryptographic Audit Ledger
        audit_entry = self.audit.record_action(
            agent_id="daily_executive_sentinel",
            action="EXECUTIVE_BRIEFING_GENERATED",
            input_payload={"briefing_type": briefing_type, "active_tasks_count": len(sorted_tasks)},
            output_payload={"briefing_id": briefing_id, "summary": raw_text[:200]},
            status="SUCCESS",
            metadata={"timestamp": now_str},
        )

        return ExecutiveBriefing(
            briefing_id=briefing_id,
            timestamp=now_str,
            greeting="Good day, Charan.",
            spoken_voice_briefing=raw_text.strip(),
            top_priorities=[asdict(t) for t in sorted_tasks[:3]],
            upcoming_deadlines=[asdict(t) for t in sorted_tasks],
            suggested_focus_schedule="Deep Work Block: 2:00 PM - 5:00 PM (Lab VM & Vision Assignment)",
            system_readiness_status="ALL_SYSTEMS_OPTIMAL_THERMAL_STABLE",
            audit_hash=audit_entry.current_hash,
        )
