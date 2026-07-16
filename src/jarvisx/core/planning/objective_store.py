import sqlite3
import logging
import uuid
import json
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ObjectiveStore:
    """
    Persistent storage layer for objectives, milestones, tasks, and snapshots.
    Uses SQLite WAL mode for crash-safe, concurrent access.
    """
    def __init__(self, db_path="var/objectives.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # Return dicts instead of tuples for ease of use
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS visions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'created',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS objectives (
                id TEXT PRIMARY KEY,
                vision_id TEXT,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'created',
                priority TEXT DEFAULT 'normal',
                objective_type TEXT DEFAULT 'engineering',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(vision_id) REFERENCES visions(id)
            );
            
            CREATE TABLE IF NOT EXISTS milestones (
                id TEXT PRIMARY KEY,
                objective_id TEXT,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'created',
                FOREIGN KEY(objective_id) REFERENCES objectives(id)
            );
            
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                milestone_id TEXT,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'created',
                assigned_agent TEXT,
                assigned_team TEXT,
                started_at DATETIME,
                last_heartbeat DATETIME,
                lease_expiry DATETIME,
                FOREIGN KEY(milestone_id) REFERENCES milestones(id)
            );
            
            CREATE TABLE IF NOT EXISTS dependencies (
                task_id TEXT,
                depends_on_task_id TEXT,
                PRIMARY KEY (task_id, depends_on_task_id),
                FOREIGN KEY(task_id) REFERENCES tasks(id),
                FOREIGN KEY(depends_on_task_id) REFERENCES tasks(id)
            );
            
            CREATE TABLE IF NOT EXISTS worker_assignments (
                worker_id TEXT PRIMARY KEY,
                task_id TEXT,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            );
            
            CREATE TABLE IF NOT EXISTS retry_history (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                failure_reason TEXT,
                retry_strategy TEXT,
                failed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            );
            
            CREATE TABLE IF NOT EXISTS task_events (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                event_type TEXT,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            );
            
            CREATE TABLE IF NOT EXISTS objective_snapshots (
                id TEXT PRIMARY KEY,
                objective_id TEXT,
                state_dump TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(objective_id) REFERENCES objectives(id)
            );
        ''')
        self.conn.commit()

    def get_objective(self, objective_id: str) -> Dict[str, Any]:
        cursor = self.conn.execute("SELECT * FROM objectives WHERE id = ?", (objective_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
        
    def list_active_objectives(self) -> List[Dict[str, Any]]:
        cursor = self.conn.execute("SELECT * FROM objectives WHERE status NOT IN ('completed', 'failed', 'cancelled', 'archived')")
        return [dict(row) for row in cursor.fetchall()]

    def execute_transaction(self, queries: List[tuple]):
        """Executes a list of (sql, params) in a single transaction."""
        try:
            for sql, params in queries:
                self.conn.execute(sql, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Transaction failed: {e}")
            raise

    def save_snapshot(self, objective_id: str, state: dict):
        self.conn.execute(
            "INSERT INTO objective_snapshots (id, objective_id, state_dump) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), objective_id, json.dumps(state))
        )
        self.conn.commit()

    def get_latest_snapshot(self, objective_id: str) -> dict:
        cursor = self.conn.execute(
            "SELECT state_dump FROM objective_snapshots WHERE objective_id = ? ORDER BY created_at DESC LIMIT 1",
            (objective_id,)
        )
        row = cursor.fetchone()
        return json.loads(row["state_dump"]) if row else {}
