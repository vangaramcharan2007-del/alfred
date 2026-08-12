from __future__ import annotations
import os
import json
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

class MissionPersistenceManager:
    def __init__(self, db_dir: Optional[str] = None):
        self.db_dir = Path(db_dir or "var/db")
        self.db_dir.mkdir(parents=True, exist_ok=True)

        self.missions_db_path = self.db_dir / "missions.db"
        self.executions_db_path = self.db_dir / "executions.db"
        self.failures_db_path = self.db_dir / "failures.db"

        self._init_schemas()

    def _init_schemas(self):
        # 1. missions.db
        with sqlite3.connect(self.missions_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS missions (
                    mission_id TEXT PRIMARY KEY,
                    title TEXT,
                    user_request TEXT,
                    intent TEXT,
                    capability TEXT,
                    provider TEXT,
                    status TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)
            conn.commit()

        # 2. executions.db
        with sqlite3.connect(self.executions_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    mission_id TEXT,
                    timeline TEXT,
                    capability_trace TEXT,
                    token_usage TEXT,
                    files_changed TEXT,
                    tests_executed TEXT,
                    git_changes TEXT,
                    duration REAL,
                    created_at REAL
                )
            """)
            conn.commit()

        # 3. failures.db
        with sqlite3.connect(self.failures_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS failures (
                    failure_id TEXT PRIMARY KEY,
                    mission_id TEXT,
                    step TEXT,
                    error_message TEXT,
                    failure_category TEXT,
                    details TEXT,
                    timestamp REAL
                )
            """)
            try:
                conn.execute("ALTER TABLE failures ADD COLUMN failure_category TEXT")
            except sqlite3.OperationalError:
                pass
            conn.commit()

        # 4. mission_checkpoints table in missions.db
        with sqlite3.connect(self.missions_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mission_checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    mission_id TEXT UNIQUE,
                    goal TEXT,
                    current_step_index INTEGER,
                    plan_json TEXT,
                    completed_results_json TEXT,
                    status TEXT,
                    failure_category TEXT,
                    updated_at REAL
                )
            """)
            conn.commit()

    def record_mission(self, mission_data: Dict[str, Any]) -> None:
        with sqlite3.connect(self.missions_db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO missions
                (mission_id, title, user_request, intent, capability, provider, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mission_data.get("mission_id"),
                mission_data.get("title", ""),
                mission_data.get("user_request", ""),
                mission_data.get("intent", "engineering"),
                mission_data.get("capability", "coding.agent"),
                mission_data.get("provider", "goose"),
                mission_data.get("status", "PENDING"),
                mission_data.get("created_at", time.time()),
                time.time()
            ))
            conn.commit()

    def record_execution(self, execution_data: Dict[str, Any]) -> None:
        with sqlite3.connect(self.executions_db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO executions
                (execution_id, mission_id, timeline, capability_trace, token_usage, files_changed, tests_executed, git_changes, duration, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_data.get("execution_id", f"exec_{execution_data.get('mission_id', 'unknown')}"),
                execution_data.get("mission_id"),
                json.dumps(execution_data.get("timeline", [])),
                json.dumps(execution_data.get("capability_trace", [])),
                json.dumps(execution_data.get("token_usage", {})),
                json.dumps(execution_data.get("files_changed", [])),
                json.dumps(execution_data.get("tests_executed", {})),
                json.dumps(execution_data.get("git_changes", {})),
                execution_data.get("duration", 0.0),
                time.time()
            ))
            conn.commit()

    def record_failure(self, failure_data: Dict[str, Any]) -> None:
        with sqlite3.connect(self.failures_db_path) as conn:
            conn.execute("""
                INSERT INTO failures (failure_id, mission_id, step, error_message, failure_category, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                failure_data.get("failure_id", f"fail_{time.time()}"),
                failure_data.get("mission_id", "unknown"),
                failure_data.get("step", "unknown"),
                failure_data.get("error_message", "Execution error"),
                failure_data.get("failure_category", "FATAL"),
                json.dumps(failure_data.get("details", {})),
                time.time()
            ))
            conn.commit()

    def save_checkpoint(
        self,
        mission_id: str,
        goal: str,
        current_step_index: int,
        plan_data: Dict[str, Any],
        completed_results: Dict[str, Any],
        status: str = "running",
        failure_category: Optional[str] = None,
    ) -> str:
        """Save restart-safe checkpoint for an in-flight or interrupted mission."""
        checkpoint_id = f"ckpt_{mission_id}_{current_step_index}"
        with sqlite3.connect(self.missions_db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO mission_checkpoints
                (checkpoint_id, mission_id, goal, current_step_index, plan_json, completed_results_json, status, failure_category, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                checkpoint_id,
                mission_id,
                goal,
                current_step_index,
                json.dumps(plan_data),
                json.dumps(completed_results),
                status,
                failure_category,
                time.time(),
            ))
            conn.commit()
        return checkpoint_id

    def load_checkpoint(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Load latest checkpoint for a given mission_id."""
        with sqlite3.connect(self.missions_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM mission_checkpoints WHERE mission_id = ?", (mission_id,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            res["plan"] = json.loads(res["plan_json"]) if res["plan_json"] else {}
            res["completed_results"] = json.loads(res["completed_results_json"]) if res["completed_results_json"] else {}
            return res

    def list_active_checkpoints(self) -> List[Dict[str, Any]]:
        """List all active or interrupted mission checkpoints awaiting resume."""
        with sqlite3.connect(self.missions_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM mission_checkpoints WHERE status IN ('running', 'interrupted', 'replanned') ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["plan"] = json.loads(item["plan_json"]) if item["plan_json"] else {}
                item["completed_results"] = json.loads(item["completed_results_json"]) if item["completed_results_json"] else {}
                results.append(item)
            return results

    def clear_checkpoint(self, mission_id: str) -> bool:
        """Remove checkpoint once mission has finished cleanly."""
        with sqlite3.connect(self.missions_db_path) as conn:
            cursor = conn.execute("DELETE FROM mission_checkpoints WHERE mission_id = ?", (mission_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_all_missions(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.missions_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM missions ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_mission_executions(self, mission_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.executions_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM executions WHERE mission_id = ?", (mission_id,))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                r = dict(row)
                r["timeline"] = json.loads(r["timeline"]) if r["timeline"] else []
                r["capability_trace"] = json.loads(r["capability_trace"]) if r["capability_trace"] else []
                r["token_usage"] = json.loads(r["token_usage"]) if r["token_usage"] else {}
                r["files_changed"] = json.loads(r["files_changed"]) if r["files_changed"] else []
                r["tests_executed"] = json.loads(r["tests_executed"]) if r["tests_executed"] else {}
                r["git_changes"] = json.loads(r["git_changes"]) if r["git_changes"] else {}
                results.append(r)
            return results

