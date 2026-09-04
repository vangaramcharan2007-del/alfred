import logging
import sqlite3
import json
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class OpenVikingsMemoryCore:
    """
    Implements the OpenVikings Long-Term Persistent Memory architecture.
    Records semantic task outcomes for compounding intelligence.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.project_dir = Path(__file__).parent.parent.parent.parent.absolute()
        self.db_path = self.project_dir / "var" / "db" / "open_vikings_memory.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS semantic_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    task_signature TEXT,
                    solution_summary TEXT,
                    success_rate REAL
                )
            ''')
            conn.commit()

    def _push_to_ui(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def commit_memory(self, task_signature: str, solution_summary: str, success_rate: float = 1.0):
        """Saves a permanent structural memory of how a task was solved."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO semantic_memory (timestamp, task_signature, solution_summary, success_rate) VALUES (?, ?, ?, ?)",
                    (time.time(), task_signature, solution_summary, success_rate)
                )
                conn.commit()
            logger.info(f"[OpenVikings] Memory committed for signature: {task_signature}")
            self._push_to_ui("memory_event", {"status": f"Brain updated: {task_signature}"})
        except Exception as e:
            logger.error(f"[OpenVikings] Memory commit failed: {e}")

    def recall(self, query_signature: str) -> str:
        """Retrieves past solutions to avoid re-computing complex logic."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT solution_summary FROM semantic_memory WHERE task_signature LIKE ? ORDER BY timestamp DESC LIMIT 1",
                    (f"%{query_signature}%",)
                )
                row = cursor.fetchone()
                if row:
                    return row[0]
        except Exception:
            pass
        return ""
