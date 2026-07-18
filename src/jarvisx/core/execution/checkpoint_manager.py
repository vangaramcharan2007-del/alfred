"""Checkpoint Manager — handles saving and loading execution snapshots."""
import sqlite3
import json
import logging
from typing import Optional
from contextlib import closing

from jarvisx.core.execution.execution_snapshot import ExecutionSnapshot

logger = logging.getLogger(__name__)

class CheckpointManager:
    """Manages the persistence of ExecutionSnapshots to SQLite."""

    def __init__(self, db_path: str = "jarvisx_state.db"):
        self.db_path = db_path
        # Schema should already be initialized by PersistentQueue, but just in case:
        self._init_db()

    def _init_db(self):
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    objective_id TEXT PRIMARY KEY,
                    snapshot_version INTEGER,
                    serialized_snapshot TEXT,
                    timestamp REAL,
                    FOREIGN KEY (objective_id) REFERENCES objectives (objective_id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def save_checkpoint(self, snapshot: ExecutionSnapshot):
        """Save a snapshot to the database."""
        serialized = json.dumps(snapshot.to_dict())
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO checkpoints (objective_id, snapshot_version, serialized_snapshot, timestamp)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(objective_id) DO UPDATE SET
                    snapshot_version = excluded.snapshot_version,
                    serialized_snapshot = excluded.serialized_snapshot,
                    timestamp = excluded.timestamp
            """, (snapshot.objective_id, snapshot.version, serialized, snapshot.timestamp))
            conn.commit()
            logger.info(f"[Checkpoint] Saved Step {snapshot.current_step}")

    def load_checkpoint(self, objective_id: str) -> Optional[ExecutionSnapshot]:
        """Load the latest snapshot for an objective."""
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT serialized_snapshot FROM checkpoints WHERE objective_id = ?
            """, (objective_id,))
            row = cursor.fetchone()
            
            if row:
                data = json.loads(row[0])
                return ExecutionSnapshot.from_dict(data)
            return None

    def delete_checkpoint(self, objective_id: str):
        """Delete a checkpoint when an objective finishes."""
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM checkpoints WHERE objective_id = ?", (objective_id,))
            conn.commit()
