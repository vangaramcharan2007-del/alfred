"""User Goal Tracker for Jarvis X (Layer 2 - Goals).

Tracks long-term goals, short-term objectives, and deadlines with progress,
confidence, next action, and status stored in SQLite memory database.
"""

import time
import uuid
from typing import Any, Dict, List, Optional

from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider


class GoalTracker:
    """Zero-fluff production user goal tracking engine."""

    def __init__(self, memory_provider: Optional[SQLiteMemoryProvider] = None):
        self.memory = memory_provider or SQLiteMemoryProvider(db_path="var/db/memory.db")

    def add_goal(
        self,
        goal: str,
        goal_type: str = "SHORT_TERM",
        next_action: str = "Deconstruct steps",
        deadline: Optional[str] = None,
        confidence: float = 0.9,
    ) -> Dict[str, Any]:
        """Register a new long-term, short-term, or deadline goal."""
        valid_types = {"LONG_TERM", "SHORT_TERM", "DEADLINE"}
        type_clean = goal_type.upper() if goal_type.upper() in valid_types else "SHORT_TERM"
        goal_id = f"goal_{uuid.uuid4().hex[:8]}"

        entry = {
            "goal_id": goal_id,
            "goal": goal,
            "type": type_clean,
            "status": "IN_PROGRESS",
            "progress": 0.0,
            "next_action": next_action,
            "confidence": max(0.0, min(1.0, confidence)),
            "deadline": deadline or "Not specified",
            "created_at": time.time(),
        }

        self.memory.save_memory(
            category="goal",
            key=goal_id,
            value=entry,
            context={"module": "goal_tracker", "goal_type": type_clean}
        )
        return entry

    def update_goal_progress(
        self,
        goal_id: str,
        progress: float,
        status: Optional[str] = None,
        next_action: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update goal completion progress, status, and next action."""
        memories = self.memory.search_memory("goal", top_k=20)
        target = None
        for m in memories:
            if m.get("id") == goal_id or m.get("value", {}).get("goal_id") == goal_id:
                target = m
                break

        if not target:
            return {"status": "error", "reason": f"Goal ID '{goal_id}' not found"}

        val = target["value"]
        val["progress"] = max(0.0, min(1.0, progress))
        if status:
            val["status"] = status.upper()
        if progress >= 1.0:
            val["status"] = "COMPLETED"
        if next_action:
            val["next_action"] = next_action

        self.memory.save_memory(
            category="goal",
            key=goal_id,
            value=val,
            context={"module": "goal_tracker", "updated_at": time.time()}
        )
        return val

    def get_active_goals(self) -> List[Dict[str, Any]]:
        """Retrieve all active incomplete goals."""
        memories = self.memory.search_memory("goal", top_k=20)
        active = []
        for m in memories:
            val = m.get("value", {})
            if val.get("status") in ("IN_PROGRESS", "NOT_STARTED"):
                active.append(val)
        return active

    def get_due_deadlines(self) -> List[Dict[str, Any]]:
        """Retrieve upcoming deadlines and urgent objectives."""
        active = self.get_active_goals()
        deadlines = [g for g in active if g.get("type") == "DEADLINE" or g.get("deadline") != "Not specified"]
        return deadlines
