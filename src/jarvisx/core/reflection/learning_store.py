import sqlite3
import logging
import uuid
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class LearningStore:
    """
    Persistent storage for reflection lessons and historical analytics.
    Uses SQLite WAL mode.
    """
    def __init__(self, db_path="var/learning.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS lessons (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                context_id TEXT,
                lesson_data TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS worker_metrics (
                worker_id TEXT PRIMARY KEY,
                total_tasks INTEGER DEFAULT 0,
                successful_tasks INTEGER DEFAULT 0,
                failed_tasks INTEGER DEFAULT 0,
                average_duration_ms INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS strategy_evaluations (
                id TEXT PRIMARY KEY,
                objective_id TEXT,
                planning_accuracy REAL,
                execution_efficiency REAL,
                recovery_efficiency REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self.conn.commit()

    def log_lesson(self, category: str, context_id: str, data: dict):
        self.conn.execute(
            "INSERT INTO lessons (id, category, context_id, lesson_data) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), category, context_id, json.dumps(data))
        )
        self.conn.commit()

    def get_lessons(self, category: str = None, limit: int = 50) -> list:
        if category:
            cursor = self.conn.execute("SELECT * FROM lessons WHERE category = ? ORDER BY created_at DESC LIMIT ?", (category, limit))
        else:
            cursor = self.conn.execute("SELECT * FROM lessons ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
