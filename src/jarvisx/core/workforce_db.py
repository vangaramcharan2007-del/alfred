import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger("WorkforceDatabase")

class WorkforceDatabase:
    """
    Persistence layer for the workforce orchestrator.
    Handles schema migrations and task state logging.
    """
    def __init__(self, db_path="var/workforce.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS workforce_tasks (
                task_id TEXT PRIMARY KEY,
                parent_task_id TEXT,
                assigned_agent TEXT NOT NULL,
                status TEXT NOT NULL,
                worktree TEXT NOT NULL,
                branch TEXT NOT NULL,
                retries INTEGER DEFAULT 0,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                artifacts TEXT
            )
        ''')
        self.conn.commit()
        logger.info(f"Workforce database initialized at {self.db_path}")

    def upsert_task(self, task_data: dict):
        self.conn.execute('''
            INSERT INTO workforce_tasks (
                task_id, parent_task_id, assigned_agent, status, 
                worktree, branch, retries, completed_at, artifacts
            ) VALUES (
                :task_id, :parent_task_id, :assigned_agent, :status, 
                :worktree, :branch, :retries, :completed_at, :artifacts
            )
            ON CONFLICT(task_id) DO UPDATE SET
                status=excluded.status,
                retries=excluded.retries,
                completed_at=excluded.completed_at,
                artifacts=excluded.artifacts
        ''', {
            "task_id": task_data.get("task_id"),
            "parent_task_id": task_data.get("parent_task_id"),
            "assigned_agent": task_data.get("assigned_agent", "unknown"),
            "status": task_data.get("status", "PENDING"),
            "worktree": task_data.get("worktree", ""),
            "branch": task_data.get("branch", ""),
            "retries": task_data.get("retries", 0),
            "completed_at": task_data.get("completed_at"),
            "artifacts": task_data.get("artifacts", "{}")
        })
        self.conn.commit()
