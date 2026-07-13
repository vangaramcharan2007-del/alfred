import json
import sqlite3
import threading
from contextlib import closing
from pathlib import Path
from typing import Any, Optional

from jarvisx.clients.supabase_client import SupabaseClient
from jarvisx.core.health import HealthStatus
from jarvisx.core.logging import StructuredLogger
import queue
import time


class OperationalDatabase:
    """SQLite offline cache with Supabase synchronization."""
    
    def __init__(self, db_path: Path, supabase: Optional[SupabaseClient] = None, logger: Optional[StructuredLogger] = None):
        self.db_path = db_path
        self.supabase = supabase or SupabaseClient()
        self.logger = logger or StructuredLogger()
        self._init_db()
        
        # Sync worker state
        self._sync_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._sync_thread = threading.Thread(target=self._sync_worker_loop, daemon=True, name="OpDBSyncWorker")
        self._sync_thread.start()
        
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._get_connection()) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS operational_data (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    synced INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def get(self, key: str) -> Optional[dict[str, Any]]:
        with closing(self._get_connection()) as conn:
            row = conn.execute("SELECT data FROM operational_data WHERE key = ?", (key,)).fetchone()
            if row:
                return json.loads(row["data"])
        return None

    def set(self, key: str, data: dict[str, Any]) -> None:
        json_data = json.dumps(data)
        with closing(self._get_connection()) as conn:
            conn.execute("""
                INSERT INTO operational_data (key, data, synced)
                VALUES (?, ?, 0)
                ON CONFLICT(key) DO UPDATE SET
                    data=excluded.data,
                    updated_at=CURRENT_TIMESTAMP,
                    synced=0
            """, (key, json_data))
            conn.commit()
            
        self._trigger_sync(key, data)

    def _trigger_sync(self, key: str, data: dict[str, Any]) -> None:
        if not self.supabase.is_configured:
            return
        # We put tasks into the queue
        self._sync_queue.put((key, data))
            
    def _sync_worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                key, data = self._sync_queue.get(timeout=1.0)
            except queue.Empty:
                continue
                
            self._process_sync(key, data)
            self._sync_queue.task_done()
            
    def _process_sync(self, key: str, data: dict[str, Any]) -> None:
        backoff = 1
        max_backoff = 1800
        while not self._stop_event.is_set():
            try:
                record = {"id": key, "data": data}
                success, _ = self.supabase.insert("operational_data", record)
                if success:
                    with closing(self._get_connection()) as conn:
                        conn.execute("UPDATE operational_data SET synced = 1 WHERE key = ?", (key,))
                        conn.commit()
                    return # Success, exit retry loop
            except Exception as e:
                self.logger.write("warning", "op_db.sync.failed", key=key, error=str(e), backoff=backoff)
            
            # Wait with exponential backoff before retrying
            if self._stop_event.wait(backoff):
                break # Interrupted by stop event
            backoff = min(backoff * 2, max_backoff)
            
    def close(self) -> None:
        """Flushes the sync queue and shuts down the worker thread."""
        self._stop_event.set()
        if self._sync_thread.is_alive():
            self._sync_thread.join(timeout=5.0)
        
    def sync_unsynced(self) -> None:
        if not self.supabase.is_configured:
            return
            
        with closing(self._get_connection()) as conn:
            rows = conn.execute("SELECT key, data FROM operational_data WHERE synced = 0").fetchall()
            
        for row in rows:
            self._trigger_sync(row["key"], json.loads(row["data"]))

    def health(self) -> HealthStatus:
        try:
            with closing(self._get_connection()) as conn:
                conn.execute("SELECT 1")
            return HealthStatus.ok("Operational DB ready.")
        except Exception as e:
            return HealthStatus.fail(f"Operational DB error: {e}")
