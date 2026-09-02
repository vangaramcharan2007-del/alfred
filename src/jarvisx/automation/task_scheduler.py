"""
Scheduled Tasks Engine — Cron-style task scheduler for Jarvis X.
Supports one-shot timers, recurring schedules, and natural language time parsing.
"""

import logging
import threading
import time
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)


class ScheduledTask:
    def __init__(self, task_id: str, description: str, run_at: datetime,
                 action: str, args: Dict = None, recurring_minutes: int = 0):
        self.task_id = task_id
        self.description = description
        self.run_at = run_at
        self.action = action
        self.args = args or {}
        self.recurring_minutes = recurring_minutes
        self.completed = False
        self.last_run: Optional[datetime] = None


class TaskScheduler:
    """Background scheduler that runs tasks at specified times."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "TaskScheduler":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._tasks: List[ScheduledTask] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._counter = 0
        self._db_path = Path("var/db/scheduled_tasks.json")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_tasks()

    def _load_tasks(self):
        if self._db_path.exists():
            try:
                data = json.loads(self._db_path.read_text(encoding="utf-8"))
                for t in data:
                    task = ScheduledTask(
                        t["task_id"], t["description"],
                        datetime.fromisoformat(t["run_at"]),
                        t["action"], t.get("args", {}),
                        t.get("recurring_minutes", 0)
                    )
                    if not t.get("completed", False):
                        self._tasks.append(task)
            except Exception:
                pass

    def _save_tasks(self):
        data = []
        for t in self._tasks:
            data.append({
                "task_id": t.task_id, "description": t.description,
                "run_at": t.run_at.isoformat(), "action": t.action,
                "args": t.args, "recurring_minutes": t.recurring_minutes,
                "completed": t.completed
            })
        self._db_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def parse_time(self, text: str) -> Optional[datetime]:
        """Parse natural language time expressions."""
        now = datetime.now()
        text_lower = text.lower().strip()

        # "in X minutes/hours"
        m = re.search(r'in\s+(\d+)\s+(minute|min|hour|hr|second|sec)s?', text_lower)
        if m:
            val, unit = int(m.group(1)), m.group(2)
            if unit in ("hour", "hr"):
                return now + timedelta(hours=val)
            elif unit in ("minute", "min"):
                return now + timedelta(minutes=val)
            else:
                return now + timedelta(seconds=val)

        # "at HH:MM" or "at H pm/am"
        m = re.search(r'at\s+(\d{1,2}):?(\d{2})?\s*(am|pm)?', text_lower)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2) or 0)
            ampm = m.group(3)
            if ampm == "pm" and hour < 12:
                hour += 12
            elif ampm == "am" and hour == 12:
                hour = 0
            target = now.replace(hour=hour, minute=minute, second=0)
            if target <= now:
                target += timedelta(days=1)
            return target

        # "tomorrow"
        if "tomorrow" in text_lower:
            return now + timedelta(days=1)

        return None

    def add_task(self, description: str, run_at: datetime, action: str = "remind",
                 args: Dict = None, recurring_minutes: int = 0) -> ScheduledTask:
        self._counter += 1
        task = ScheduledTask(
            f"task_{self._counter}", description, run_at,
            action, args, recurring_minutes
        )
        self._tasks.append(task)
        self._save_tasks()
        logger.info(f"[Scheduler] Added: '{description}' at {run_at}")
        return task

    def list_tasks(self) -> List[Dict[str, Any]]:
        return [{"id": t.task_id, "description": t.description,
                 "run_at": t.run_at.isoformat(), "completed": t.completed}
                for t in self._tasks if not t.completed]

    def cancel_task(self, task_id: str) -> bool:
        for t in self._tasks:
            if t.task_id == task_id:
                t.completed = True
                self._save_tasks()
                return True
        return False

    def _execute_task(self, task: ScheduledTask):
        logger.info(f"[Scheduler] Firing: {task.description}")
        try:
            from jarvisx.automation.smart_notifier import SmartNotifier
            SmartNotifier.get_instance().send_custom(
                f"Reminder: {task.description}", "info"
            )
        except Exception as e:
            logger.error(f"[Scheduler] Execution error: {e}")

        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync("scheduled_task", {"description": task.description})
        except Exception:
            pass

    def _loop(self):
        while self._running:
            now = datetime.now()
            for task in self._tasks:
                if task.completed:
                    continue
                if now >= task.run_at:
                    self._execute_task(task)
                    if task.recurring_minutes > 0:
                        task.run_at = now + timedelta(minutes=task.recurring_minutes)
                        task.last_run = now
                    else:
                        task.completed = True
                    self._save_tasks()
            time.sleep(10)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="TaskScheduler")
        self._thread.start()

    def stop(self):
        self._running = False
