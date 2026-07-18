"""Persistent Queue — SQLite-backed durable objective queue."""
import sqlite3
import json
import logging
from enum import Enum
from typing import Dict, Any, List, Optional
import time
from contextlib import closing

from jarvisx.core.execution.objective_state_machine import ObjectiveStatus, ObjectiveStateMachine

logger = logging.getLogger(__name__)

class Priority(int, Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class PersistentQueue:
    """Manages the durable queuing of objectives in SQLite."""
    
    def __init__(self, db_path: str = "jarvisx_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cursor = conn.cursor()
            
            # Objectives table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS objectives (
                    objective_id TEXT PRIMARY KEY,
                    objective_text TEXT,
                    objective_data TEXT,
                    status TEXT,
                    priority INTEGER,
                    current_step INTEGER,
                    total_steps INTEGER,
                    retry_count INTEGER,
                    last_error TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)
            
            # Checkpoints table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    objective_id TEXT PRIMARY KEY,
                    snapshot_version INTEGER,
                    serialized_snapshot TEXT,
                    timestamp REAL,
                    FOREIGN KEY (objective_id) REFERENCES objectives (objective_id) ON DELETE CASCADE
                )
            """)
            
            # History table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS objective_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    objective_id TEXT,
                    event TEXT,
                    timestamp REAL,
                    duration REAL,
                    recovery_count INTEGER,
                    retry_count INTEGER,
                    FOREIGN KEY (objective_id) REFERENCES objectives (objective_id) ON DELETE CASCADE
                )
            """)
            
            # Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON objectives(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON objectives(priority)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON objectives(created_at)")
            
            conn.commit()

    def enqueue(self, objective_id: str, objective_text: str, objective_data: Dict[str, Any], priority: Priority = Priority.NORMAL):
        """Add an objective to the queue."""
        now = time.time()
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO objectives (
                    objective_id, objective_text, objective_data, status, priority, 
                    current_step, total_steps, retry_count, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                objective_id, 
                objective_text, 
                json.dumps(objective_data),
                ObjectiveStatus.QUEUED.value, 
                priority.value,
                0, 
                len(objective_data.get("steps", [])), 
                0, 
                now, 
                now
            ))
            conn.commit()

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Retrieve the next highest priority queued objective and mark it RUNNING."""
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            # We want to select the next item. SQLite doesn't have SELECT FOR UPDATE easily.
            # But we can update returning in modern SQLite, or use a two step with isolation.
            # We'll lock exclusively for this transaction.
            conn.execute("BEGIN EXCLUSIVE")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT objective_id, objective_text, objective_data, status, priority, current_step, total_steps
                FROM objectives 
                WHERE status = ?
                ORDER BY priority DESC, created_at ASC 
                LIMIT 1
            """, (ObjectiveStatus.QUEUED.value,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            objective_id = row[0]
            
            # Transition state if it was QUEUED
            if row[3] == ObjectiveStatus.QUEUED.value:
                self._update_status_internal(cursor, objective_id, row[3], ObjectiveStatus.RUNNING)
                conn.commit()
            
            return {
                "objective_id": objective_id,
                "objective_text": row[1],
                "objective_data": json.loads(row[2]),
                "status": ObjectiveStatus.RUNNING.value,
                "priority": row[4],
                "current_step": row[5],
                "total_steps": row[6]
            }

    def peek(self) -> Optional[Dict[str, Any]]:
        """View the next objective without dequeuing it."""
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT objective_id, objective_text, status, priority 
                FROM objectives 
                WHERE status = ? 
                ORDER BY priority DESC, created_at ASC 
                LIMIT 1
            """, (ObjectiveStatus.QUEUED.value,))
            
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "objective_id": row[0],
                "objective_text": row[1],
                "status": row[2],
                "priority": row[3]
            }

    def update_status(self, objective_id: str, next_state: ObjectiveStatus, last_error: Optional[str] = None):
        """Update the status of an objective using the state machine."""
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute("BEGIN EXCLUSIVE")
            cursor = conn.cursor()
            
            cursor.execute("SELECT status FROM objectives WHERE objective_id = ?", (objective_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Objective {objective_id} not found.")
                
            self._update_status_internal(cursor, objective_id, row[0], next_state, last_error)
            conn.commit()

    def _update_status_internal(self, cursor, objective_id: str, current_state_str: str, next_state: ObjectiveStatus, last_error: Optional[str] = None):
        """Internal helper to validate transition and update."""
        current_state = ObjectiveStatus(current_state_str)
        validated_state = ObjectiveStateMachine.transition(current_state, next_state)
        
        now = time.time()
        
        if last_error:
            cursor.execute("""
                UPDATE objectives 
                SET status = ?, updated_at = ?, last_error = ? 
                WHERE objective_id = ?
            """, (validated_state.value, now, last_error, objective_id))
        else:
            cursor.execute("""
                UPDATE objectives 
                SET status = ?, updated_at = ?
                WHERE objective_id = ?
            """, (validated_state.value, now, objective_id))
            
    def update_progress(self, objective_id: str, current_step: int):
        """Update the progress of an objective."""
        now = time.time()
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE objectives
                SET current_step = ?, updated_at = ?
                WHERE objective_id = ?
            """, (current_step, now, objective_id))
            conn.commit()

    def pause(self, objective_id: str):
        self.update_status(objective_id, ObjectiveStatus.PAUSED)

    def resume(self, objective_id: str):
        self.update_status(objective_id, ObjectiveStatus.QUEUED)

    def cancel(self, objective_id: str):
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute("BEGIN EXCLUSIVE")
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM objectives WHERE objective_id = ?", (objective_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Objective {objective_id} not found.")
                
            current_state = ObjectiveStatus(row[0])
            if current_state == ObjectiveStatus.FAILED:
                # Direct transition allowed
                validated_state = ObjectiveStateMachine.transition(current_state, ObjectiveStatus.CANCELLED)
            else:
                # If it's RUNNING, we can't cancel directly according to state machine. 
                # We need it to fail first, or we modify state machine to allow RUNNING -> CANCELLED.
                # The user prompt says FAILED -> CANCELLED is allowed.
                # If it's QUEUED, can we cancel it? Prompt doesn't explicitly allow QUEUED -> CANCELLED.
                # I will assume we force it through FAILED.
                try:
                    validated_state = ObjectiveStateMachine.transition(current_state, ObjectiveStatus.CANCELLED)
                except Exception:
                    # Let's enforce FAILED first
                    self._update_status_internal(cursor, objective_id, current_state.value, ObjectiveStatus.FAILED, "Cancelled by user")
                    validated_state = ObjectiveStateMachine.transition(ObjectiveStatus.FAILED, ObjectiveStatus.CANCELLED)
                    
            self._update_status_internal(cursor, objective_id, ObjectiveStatus.FAILED.value, ObjectiveStatus.CANCELLED)
            conn.commit()

    def queue_length(self, status: ObjectiveStatus = ObjectiveStatus.QUEUED) -> int:
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM objectives WHERE status = ?", (status.value,))
            return cursor.fetchone()[0]

    def get_all_by_status(self, statuses: List[ObjectiveStatus]) -> List[Dict[str, Any]]:
        status_strs = [s.value for s in statuses]
        placeholders = ",".join("?" * len(status_strs))
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT objective_id, objective_text, objective_data, status, priority, current_step, total_steps
                FROM objectives
                WHERE status IN ({placeholders})
                ORDER BY created_at ASC
            """, status_strs)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "objective_id": row[0],
                    "objective_text": row[1],
                    "objective_data": json.loads(row[2]),
                    "status": row[3],
                    "priority": row[4],
                    "current_step": row[5],
                    "total_steps": row[6]
                })
            return results
