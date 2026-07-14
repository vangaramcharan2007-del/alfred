import sqlite3
import logging
import json
from pathlib import Path

logger = logging.getLogger("SyncRuntime")

class SyncRuntime:
    def __init__(self, db_path="var/sync.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None

    def initialize_wal(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_hash TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        logger.info(f"SyncEngine initialized WAL at {self.db_path}.")

    def enqueue_event(self, event_hash: str, event_type: str, payload: dict):
        try:
            self.conn.execute(
                "INSERT INTO events (event_hash, event_type, payload) VALUES (?, ?, ?)",
                (event_hash, event_type, json.dumps(payload))
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            logger.debug(f"Duplicate event ignored: {event_hash}")

    def get_events_for_replay(self) -> list:
        cursor = self.conn.execute("SELECT event_hash, event_type, payload FROM events ORDER BY timestamp ASC")
        return [{"hash": row[0], "type": row[1], "payload": json.loads(row[2])} for row in cursor.fetchall()]

    def flush_wal(self):
        if self.conn:
            self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            self.conn.close()
            logger.info("Sync WAL flushed and connection closed.")
