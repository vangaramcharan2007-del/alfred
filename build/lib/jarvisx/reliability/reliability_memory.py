"""Persistent SQLite Store for Phase 98 Reliability Kernel and Evolution Ledger."""

from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from jarvisx.reliability.models import (
    BackupSnapshot,
    CrashEvent,
    EvolutionEvent,
    HealthState,
    RecoveryAction,
)


class ReliabilityMemory:
    """Dedicated SQLite Store for health heartbeats, crash history, snapshot manifests, and the Evolution Ledger."""

    def __init__(self, db_path: str = "var/db/reliability.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_meta (
                    version TEXT PRIMARY KEY,
                    upgraded_at REAL
                )
            """)
            cur.execute("INSERT OR IGNORE INTO schema_meta (version, upgraded_at) VALUES ('v1.0', ?)", (time.time(),))

            cur.execute("""
                CREATE TABLE IF NOT EXISTS health_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT,
                    memory_rss_mb REAL,
                    cpu_percent REAL,
                    active_threads INTEGER,
                    uptime_seconds REAL,
                    database_status_json TEXT,
                    latency_ms REAL,
                    queue_depth INTEGER,
                    last_error TEXT,
                    timestamp REAL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS crash_events (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    component TEXT,
                    exception_type TEXT,
                    stack_trace TEXT,
                    recovery_action TEXT
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS backup_snapshots (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    snapshot_dir TEXT,
                    manifest_json TEXT,
                    size_bytes INTEGER,
                    status TEXT
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS evolution_events (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    component TEXT,
                    old_behavior TEXT,
                    new_behavior TEXT,
                    reason TEXT,
                    validation_result TEXT,
                    impact_delta TEXT
                )
            """)
            conn.commit()

    def record_health(self, state: HealthState) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO health_events
                (status, memory_rss_mb, cpu_percent, active_threads, uptime_seconds, database_status_json, latency_ms, queue_depth, last_error, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.status,
                state.memory_rss_mb,
                state.cpu_percent,
                state.active_threads,
                state.uptime_seconds,
                json.dumps(state.database_status),
                state.latency_ms,
                state.queue_depth,
                state.last_error,
                time.time(),
            ))
            conn.commit()

    def get_latest_health(self) -> Optional[HealthState]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT status, memory_rss_mb, cpu_percent, active_threads, uptime_seconds, database_status_json, latency_ms, queue_depth, last_error
                FROM health_events ORDER BY id DESC LIMIT 1
            """)
            row = cur.fetchone()
            if not row:
                return None
            return HealthState(
                status=row[0],
                memory_rss_mb=row[1],
                cpu_percent=row[2],
                active_threads=row[3],
                uptime_seconds=row[4],
                database_status=json.loads(row[5]),
                latency_ms=row[6],
                queue_depth=row[7],
                last_error=row[8],
            )

    def record_crash(self, event: CrashEvent) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO crash_events (id, timestamp, component, exception_type, stack_trace, recovery_action)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event.id,
                event.timestamp,
                event.component,
                event.exception_type,
                event.stack_trace,
                event.recovery_action.value,
            ))
            conn.commit()

    def list_crashes(self) -> List[CrashEvent]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, timestamp, component, exception_type, stack_trace, recovery_action FROM crash_events ORDER BY timestamp DESC")
            return [
                CrashEvent(
                    id=r[0],
                    timestamp=r[1],
                    component=r[2],
                    exception_type=r[3],
                    stack_trace=r[4],
                    recovery_action=RecoveryAction(r[5]),
                )
                for r in cur.fetchall()
            ]

    def record_snapshot(self, snapshot: BackupSnapshot) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO backup_snapshots (id, timestamp, snapshot_dir, manifest_json, size_bytes, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                snapshot.id,
                snapshot.timestamp,
                snapshot.snapshot_dir,
                json.dumps(snapshot.checksum_manifest),
                snapshot.size_bytes,
                snapshot.status,
            ))
            conn.commit()

    def list_snapshots(self) -> List[BackupSnapshot]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, timestamp, snapshot_dir, manifest_json, size_bytes, status FROM backup_snapshots ORDER BY timestamp DESC")
            return [
                BackupSnapshot(
                    id=r[0],
                    timestamp=r[1],
                    snapshot_dir=r[2],
                    checksum_manifest=json.loads(r[3]),
                    size_bytes=r[4],
                    status=r[5],
                )
                for r in cur.fetchall()
            ]

    def record_evolution(self, event: EvolutionEvent) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO evolution_events (id, timestamp, component, old_behavior, new_behavior, reason, validation_result, impact_delta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id,
                event.timestamp,
                event.component,
                event.old_behavior,
                event.new_behavior,
                event.reason,
                event.validation_result,
                event.impact_delta,
            ))
            conn.commit()

    def list_evolutions(self) -> List[EvolutionEvent]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, timestamp, component, old_behavior, new_behavior, reason, validation_result, impact_delta FROM evolution_events ORDER BY timestamp DESC")
            return [
                EvolutionEvent(
                    id=r[0],
                    timestamp=r[1],
                    component=r[2],
                    old_behavior=r[3],
                    new_behavior=r[4],
                    reason=r[5],
                    validation_result=r[6],
                    impact_delta=r[7],
                )
                for r in cur.fetchall()
            ]
