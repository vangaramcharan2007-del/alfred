"""
AEGIS Memory Core - Persistent Encapsulated SQLite Database Layer
Stores physiological vital logs, Eye Aspect Ratio (EAR) fatigue events,
and contextual conversation history.
"""

import sqlite3
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timezone


class AegisMemory:
    """
    Encapsulated Persistent Memory Layer for AEGIS.
    Tracks vitals, optical rPPG signals, and conversational context in SQLite.
    """

    def __init__(self, db_path: str = "aegis_core.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_tables()

    def _initialize_tables(self) -> None:
        """Initialize database schema with WAL mode for fast concurrent operations."""
        self.cursor.execute("PRAGMA journal_mode=WAL;")
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vitals_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                heart_rate REAL,
                eye_aspect_ratio REAL,
                fatigue_flag BOOLEAN,
                rppg_signal REAL DEFAULT 0.0
            );
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT,
                content TEXT
            );
        """)
        self.conn.commit()

    def log_vitals(
        self,
        hr: float,
        ear: float,
        is_fatigued: bool,
        rppg_signal: float = 0.0
    ) -> int:
        """
        Log an instantaneous biometric snapshot into persistent storage.
        """
        self.cursor.execute(
            """
            INSERT INTO vitals_log (heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal)
            VALUES (?, ?, ?, ?)
            """,
            (float(hr), float(ear), int(is_fatigued), float(rppg_signal))
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_recent_baseline(self, limit: int = 50) -> List[Tuple[float, float, int, float]]:
        """
        Fetch recent vital snapshots to calculate rolling averages.
        Returns: List of tuples (heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal)
        """
        self.cursor.execute(
            """
            SELECT heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal
            FROM vitals_log
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        return self.cursor.fetchall()

    def get_latest_vital(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve the single most recent vital log entry.
        """
        self.cursor.execute(
            """
            SELECT timestamp, heart_rate, eye_aspect_ratio, fatigue_flag, rppg_signal
            FROM vitals_log
            ORDER BY id DESC
            LIMIT 1
            """
        )
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "timestamp": row[0],
            "heart_rate": float(row[1]),
            "eye_aspect_ratio": float(row[2]),
            "fatigue_flag": bool(row[3]),
            "rppg_signal": float(row[4])
        }

    def add_conversation(self, role: str, content: str) -> None:
        """
        Append a conversational turn into persistent memory context.
        """
        self.cursor.execute(
            "INSERT INTO memory_context (role, content) VALUES (?, ?)",
            (role, content)
        )
        self.conn.commit()

    def get_conversation_context(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Fetch the most recent dialogue context formatted for LLM prompts.
        """
        self.cursor.execute(
            """
            SELECT role, content
            FROM memory_context
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = self.cursor.fetchall()
        # Return in chronological order
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def clear_memory(self) -> None:
        """Clear logs (used for testing)."""
        self.cursor.execute("DELETE FROM vitals_log;")
        self.cursor.execute("DELETE FROM memory_context;")
        self.conn.commit()

    def close(self) -> None:
        """Close SQLite connection."""
        self.conn.close()
