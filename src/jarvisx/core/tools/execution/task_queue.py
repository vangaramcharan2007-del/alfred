import asyncio
import sqlite3
import uuid
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TaskState(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    RETRYING = "RETRYING"

class TaskQueue:
    """
    Background job queue with SQLite persistence.
    """
    def __init__(self, db_path="var/task_queue.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        self.queue = asyncio.Queue()
        self._running = False
        
    def _init_db(self):
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                state TEXT NOT NULL,
                retries INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self.conn.commit()

    def submit(self, payload: Dict[str, Any]) -> str:
        task_id = str(uuid.uuid4())
        state = TaskState.PENDING.value
        self.conn.execute(
            "INSERT INTO tasks (id, payload, state) VALUES (?, ?, ?)",
            (task_id, json.dumps(payload), state)
        )
        self.conn.commit()
        # Non-blocking queue push for worker loop
        try:
            self.queue.put_nowait(task_id)
        except Exception as e:
            logger.error(f"Queue put error: {e}")
        return task_id

    def update_state(self, task_id: str, state: TaskState):
        self.conn.execute("UPDATE tasks SET state = ? WHERE id = ?", (state.value, task_id))
        self.conn.commit()

    def get_task(self, task_id: str) -> Dict[str, Any]:
        cursor = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d["payload"] = json.loads(d["payload"])
            return d
        return None
