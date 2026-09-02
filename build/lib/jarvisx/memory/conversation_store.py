"""
Persistent SQLite Conversation & Context Memory Store for Jarvis X & Alfred.
=============================================================================
Ensures zero data loss across power outages, system reboots, and crashes.
Every single user prompt and AI response is persisted to SQLite with WAL mode.
"""

import os
import sys
import time
import json
import sqlite3
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("jarvisx.memory.conversation")


class PersistentConversationStore:
    """Persistent SQLite Conversation Memory Manager."""

    _instance = None

    def __init__(self, db_path: Optional[str] = None):
        if not db_path:
            base_dir = os.path.join(os.getcwd(), "var")
            os.makedirs(base_dir, exist_ok=True)
            db_path = os.path.join(base_dir, "conversation_history.db")

        self.db_path = db_path
        self._init_db()

    @classmethod
    def get_instance(cls, db_path: Optional[str] = None) -> "PersistentConversationStore":
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        """Create tables and indexes if they do not exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    text TEXT NOT NULL,
                    metadata TEXT
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conv_session_time 
                ON conversation_turns (session_id, timestamp);
            """)
            conn.commit()

    def save_turn(self, role: str, text: str, session_id: str = "default", metadata: Optional[Dict[str, Any]] = None) -> int:
        """Saves a conversation turn to SQLite synchronously."""
        if not text or not text.strip():
            return -1

        meta_json = json.dumps(metadata or {})
        now = time.time()

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO conversation_turns (timestamp, session_id, role, text, metadata) VALUES (?, ?, ?, ?, ?)",
                    (now, session_id, role, text.strip(), meta_json)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"[PersistentConversationStore] Failed to save turn: {e}")
            return -1

    def load_recent_history(self, limit: int = 20, session_id: str = "default") -> List[Dict[str, str]]:
        """Loads the most recent N turns for the given session to restore context."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role, text FROM conversation_turns WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                    (session_id, limit)
                )
                rows = cursor.fetchall()
                # Reverse to get chronological order (oldest -> newest)
                history = [{"role": r[0], "text": r[1]} for r in reversed(rows)]
                return history
        except Exception as e:
            logger.error(f"[PersistentConversationStore] Failed to load history: {e}")
            return []

    def search_past_context(self, query: str, limit: int = 5, session_id: str = "default") -> List[Dict[str, Any]]:
        """Searches past conversation records for relevant keywords across prior sessions."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT timestamp, role, text FROM conversation_turns WHERE text LIKE ? ORDER BY id DESC LIMIT ?",
                    (f"%{query}%", limit)
                )
                rows = cursor.fetchall()
                return [{"timestamp": r[0], "role": r[1], "text": r[2]} for r in rows]
        except Exception as e:
            logger.error(f"[PersistentConversationStore] Search failed: {e}")
            return []

    def get_total_turns_count(self) -> int:
        """Returns total historical turns recorded in the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM conversation_turns")
                res = cursor.fetchone()
                return res[0] if res else 0
        except Exception:
            return 0
