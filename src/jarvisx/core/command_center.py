"""
Personal Command Center — The Unified Brain for Alfred & Friday.
Shares long-term memory, goals, schedule, active tasks, notifications, and context.
Alfred handles engineering/coding/automation; Friday handles academics/life/planning.
"""
from __future__ import annotations
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider
from friday.persistence import FridayPersistenceManager


class PersonalCommandCenter:
    """
    Unified brain controller providing shared memory, scheduling, and context routing.
    """
    _instance: Optional[PersonalCommandCenter] = None

    def __init__(self, db_dir: Optional[str] = None):
        self.db_dir = Path(db_dir or "var/db")
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.memory = SQLiteMemoryProvider(db_path=str(self.db_dir / "memory.db"))
        self.friday_db = FridayPersistenceManager(db_path=str(self.db_dir / "friday.db"))
        self.active_context: Dict[str, Any] = {
            "current_mode": "IDLE",
            "active_project": "Jarvis X",
            "session_start": time.time()
        }

    @classmethod
    def get_instance(cls) -> PersonalCommandCenter:
        if cls._instance is None:
            cls._instance = PersonalCommandCenter()
        return cls._instance

    async def query_brain(self, query: str) -> Dict[str, Any]:
        """Search across shared memory, goals, schedule, and academics."""
        mem_results = await self.memory.search(query, limit=3)
        schedule = self.friday_db.get_schedule()
        assignments = self.friday_db.get_assignments()

        # Find matching schedule or assignment
        matching_sched = [s for s in schedule if query.lower() in s.get("activity", "").lower()]
        matching_assign = [a for a in assignments if query.lower() in a.get("title", "").lower() or query.lower() in a.get("subject", "").lower()]

        return {
            "status": "SUCCESS",
            "query": query,
            "memory_matches": mem_results,
            "schedule_matches": matching_sched,
            "assignment_matches": matching_assign
        }

    def set_mode(self, mode: str) -> Dict[str, Any]:
        self.active_context["current_mode"] = mode
        self.active_context["mode_updated_at"] = time.time()
        return {"status": "SUCCESS", "current_mode": mode}
