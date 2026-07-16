import logging
import sqlite3
from pathlib import Path
import time
import uuid

logger = logging.getLogger(__name__)

class CheckpointManager:
    """
    Allows user to save/restore explicit context milestones.
    """
    def __init__(self, db_path="var/memory.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                context_dump TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_checkpoint(self, name: str, context_dump: str):
        self.conn.execute(
            "INSERT INTO checkpoints (id, name, context_dump) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), name, context_dump)
        )
        self.conn.commit()
        logger.info(f"Saved checkpoint: {name}")

    def restore_checkpoint(self, name: str) -> str:
        cursor = self.conn.execute("SELECT context_dump FROM checkpoints WHERE name = ? ORDER BY timestamp DESC LIMIT 1", (name,))
        row = cursor.fetchone()
        return row[0] if row else None
