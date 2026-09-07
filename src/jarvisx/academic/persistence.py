"""Academic Sentinel Persistence Manager.

Maintains SQLite state for tasks, alerts, channel sync checkpoints,
and deduplication filters in `var/db/academic_sentinel.db`.
"""

from __future__ import annotations
import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional

from jarvisx.academic.models import AcademicTask, AlertEvent, TaskStatus

logger = logging.getLogger("jarvisx.academic.persistence")


class AcademicPersistenceManager:
    """Manages SQLite storage and historical query interfaces for Academic Sentinel."""

    def __init__(self, db_path: str = "var/db/academic_sentinel.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS academic_tasks (
                    task_id TEXT PRIMARY KEY,
                    channel TEXT NOT NULL,
                    course_code TEXT NOT NULL,
                    course_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    deadline_epoch REAL NOT NULL,
                    priority TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    faculty_name TEXT,
                    questions_json TEXT,
                    solution_text TEXT,
                    generated_code_json TEXT,
                    compiled_docx TEXT,
                    compiled_pdf TEXT,
                    submission_link TEXT,
                    score_achieved REAL,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS academic_alerts (
                    event_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    urgency TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    delivered INTEGER NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    def save_task(self, task: AcademicTask):
        """Inserts or updates an AcademicTask in the database."""
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO academic_tasks (
                    task_id, channel, course_code, course_name, title, description,
                    deadline_epoch, priority, task_type, faculty_name, questions_json,
                    solution_text, generated_code_json, compiled_docx, compiled_pdf,
                    submission_link, score_achieved, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id,
                task.channel.value,
                task.course_code,
                task.course_name,
                task.title,
                task.description,
                task.deadline_epoch,
                task.priority.value,
                task.task_type.value,
                task.faculty_name,
                json.dumps(task.questions),
                task.solution_text,
                json.dumps(task.generated_code),
                task.compiled_docx,
                task.compiled_pdf,
                task.submission_link,
                task.score_achieved,
                task.status.value,
                task.created_at,
                time.time()
            ))
            conn.commit()

    def get_task(self, task_id: str) -> Optional[AcademicTask]:
        """Retrieves a single task by ID."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM academic_tasks WHERE task_id = ?", (task_id,)).fetchone()
            if row:
                return self._row_to_task(row)
        return None

    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> List[AcademicTask]:
        """Retrieves all tasks, optionally filtered by status."""
        tasks: List[AcademicTask] = []
        query = "SELECT * FROM academic_tasks"
        params = ()
        if status:
            query += " WHERE status = ?"
            params = (status.value,)
        query += " ORDER BY deadline_epoch ASC"

        with self._get_conn() as conn:
            for row in conn.execute(query, params).fetchall():
                tasks.append(self._row_to_task(row))
        return tasks

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[AcademicTask]:
        """Alias for get_all_tasks."""
        return self.get_all_tasks(status=status)

    def record_alert(self, alert: AlertEvent):
        """Records an alert event in the ledger."""
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO academic_alerts (
                    event_id, task_id, channel, urgency, title, message, delivered, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.event_id,
                alert.task_id,
                alert.channel.value,
                alert.urgency.value,
                alert.title,
                alert.message,
                1 if alert.delivered else 0,
                alert.timestamp
            ))
            conn.commit()

    def _row_to_task(self, row: sqlite3.Row) -> AcademicTask:
        d = dict(row)
        d["questions"] = json.loads(d.pop("questions_json") or "[]")
        d["generated_code"] = json.loads(d.pop("generated_code_json") or "{}")
        return AcademicTask.from_dict(d)
