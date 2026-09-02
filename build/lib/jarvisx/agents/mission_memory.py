"""Persistent Mission Memory for Phase 91 Autonomous Mission Brain."""

from __future__ import annotations
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class MissionMemory:
    """Persistent storage for autonomous missions, action history, and learned patterns."""

    def __init__(self, db_path: str = "var/db/memory.db"):
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mission_memory (
                    mission_id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER DEFAULT 1,
                    successful_actions TEXT,
                    failed_actions TEXT,
                    artifacts TEXT,
                    learned_context TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)
            conn.commit()

    def save_mission(
        self,
        mission_id: str,
        goal: str,
        status: str,
        successful_actions: Optional[List[str]] = None,
        failed_actions: Optional[List[str]] = None,
        artifacts: Optional[List[str]] = None,
        learned_context: Optional[Dict[str, Any]] = None,
        attempts: int = 1,
    ) -> None:
        """Persist or update mission state in database."""
        now = time.time()
        succ_json = json.dumps(successful_actions or [])
        fail_json = json.dumps(failed_actions or [])
        art_json = json.dumps(artifacts or [])
        ctx_json = json.dumps(learned_context or {})

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO mission_memory (
                    mission_id, goal, status, attempts, successful_actions,
                    failed_actions, artifacts, learned_context, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(mission_id) DO UPDATE SET
                    status=excluded.status,
                    attempts=excluded.attempts,
                    successful_actions=excluded.successful_actions,
                    failed_actions=excluded.failed_actions,
                    artifacts=excluded.artifacts,
                    learned_context=excluded.learned_context,
                    updated_at=excluded.updated_at
            """, (mission_id, goal, status, attempts, succ_json, fail_json, art_json, ctx_json, now, now))
            conn.commit()

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored mission record by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM mission_memory WHERE mission_id = ?", (mission_id,)).fetchone()
            if not row:
                return None
            return {
                "mission_id": row["mission_id"],
                "goal": row["goal"],
                "status": row["status"],
                "attempts": row["attempts"],
                "successful_actions": json.loads(row["successful_actions"]),
                "failed_actions": json.loads(row["failed_actions"]),
                "artifacts": json.loads(row["artifacts"]),
                "learned_context": json.loads(row["learned_context"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
