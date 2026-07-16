import sqlite3
import logging
from pathlib import Path
import time
import uuid

logger = logging.getLogger(__name__)

class ConversationStore:
    """
    Working/Session Memory: Stores voice conversations, transcripts, 
    and timestamps for semantic retrieval across reboots.
    """
    def __init__(self, db_path="var/memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS transcripts (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                speaker TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                session_id TEXT PRIMARY KEY,
                summary TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def log_transcript(self, session_id: str, speaker: str, text: str):
        try:
            self.conn.execute(
                "INSERT INTO transcripts (id, session_id, speaker, text) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), session_id, speaker, text)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log transcript: {e}")

    def get_recent_transcripts(self, limit: int = 20) -> list:
        cursor = self.conn.execute(
            "SELECT speaker, text, timestamp FROM transcripts ORDER BY timestamp DESC LIMIT ?", 
            (limit,)
        )
        rows = cursor.fetchall()
        return [{"speaker": r[0], "text": r[1], "timestamp": r[2]} for r in reversed(rows)]

    def get_session_summary(self, session_id: str) -> str:
        cursor = self.conn.execute(
            "SELECT summary FROM summaries WHERE session_id = ?", 
            (session_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else ""

    def save_summary(self, session_id: str, summary: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO summaries (session_id, summary) VALUES (?, ?)",
            (session_id, summary)
        )
        self.conn.commit()
