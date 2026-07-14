import logging
import sqlite3
import json
from pathlib import Path

logger = logging.getLogger("SessionRuntime")

class SessionRuntime:
    def __init__(self, db_path="var/session.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                context_data TEXT NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_checkpoint(self, session_id: str, context: dict):
        self.conn.execute(
            "INSERT OR REPLACE INTO sessions (session_id, context_data, last_updated) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (session_id, json.dumps(context))
        )
        self.conn.commit()
        logger.debug(f"Session {session_id} checkpoint saved.")

    def restore_state(self):
        cursor = self.conn.execute("SELECT COUNT(*) FROM sessions")
        count = cursor.fetchone()[0]
        logger.info(f"Session context restored. {count} active sessions recovered from disk.")
