"""Persistent SQLite Store for Phase 99 Security & Trust Layer."""

from __future__ import annotations
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from jarvisx.security.models import AuditEntry, PermissionScope, SecretItem


class SecurityMemory:
    """Dedicated SQLite Store for active permissions, encrypted secrets, and hash-chained audit events."""

    def __init__(self, db_path: str = "var/db/security.db"):
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
                CREATE TABLE IF NOT EXISTS permissions (
                    id TEXT PRIMARY KEY,
                    agent TEXT,
                    capability TEXT,
                    scope TEXT,
                    expires REAL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS secrets (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE,
                    encrypted_blob_b64 TEXT,
                    nonce_b64 TEXT,
                    masked_preview TEXT,
                    created_at REAL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    actor TEXT,
                    action TEXT,
                    risk_score INTEGER,
                    decision TEXT,
                    previous_hash TEXT,
                    current_hash TEXT
                )
            """)
            conn.commit()

    def save_permission(self, perm_id: str, agent: str, capability: str, scope: str, expires: float) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO permissions (id, agent, capability, scope, expires)
                VALUES (?, ?, ?, ?, ?)
            """, (perm_id, agent, capability, scope, expires))
            conn.commit()

    def list_permissions(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, agent, capability, scope, expires FROM permissions")
            return [
                {
                    "id": r[0],
                    "agent": r[1],
                    "capability": r[2],
                    "scope": r[3],
                    "expires": r[4],
                }
                for r in cur.fetchall()
            ]

    def save_secret(self, secret: SecretItem) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO secrets (id, name, encrypted_blob_b64, nonce_b64, masked_preview, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                secret.key_name,
                secret.key_name,
                secret.encrypted_blob_b64,
                secret.nonce_b64,
                secret.masked_preview,
                secret.created_at,
            ))
            conn.commit()

    def get_secret(self, name: str) -> Optional[SecretItem]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, encrypted_blob_b64, nonce_b64, masked_preview, created_at FROM secrets WHERE name = ?", (name,))
            row = cur.fetchone()
            if not row:
                return None
            return SecretItem(
                key_name=row[0],
                encrypted_blob_b64=row[1],
                nonce_b64=row[2],
                masked_preview=row[3],
                created_at=row[4],
            )

    def list_secrets(self) -> List[SecretItem]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, encrypted_blob_b64, nonce_b64, masked_preview, created_at FROM secrets")
            return [
                SecretItem(
                    key_name=r[0],
                    encrypted_blob_b64=r[1],
                    nonce_b64=r[2],
                    masked_preview=r[3],
                    created_at=r[4],
                )
                for r in cur.fetchall()
            ]

    def append_audit_entry(self, entry: AuditEntry) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO audit_events (id, timestamp, actor, action, risk_score, decision, previous_hash, current_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id,
                entry.timestamp,
                entry.actor,
                entry.action,
                entry.risk_score,
                entry.decision,
                entry.previous_hash,
                entry.current_hash,
            ))
            conn.commit()

    def list_audit_entries(self) -> List[AuditEntry]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, timestamp, actor, action, risk_score, decision, previous_hash, current_hash FROM audit_events ORDER BY timestamp ASC")
            return [
                AuditEntry(
                    id=r[0],
                    timestamp=r[1],
                    actor=r[2],
                    action=r[3],
                    risk_score=r[4],
                    decision=r[5],
                    previous_hash=r[6],
                    current_hash=r[7],
                )
                for r in cur.fetchall()
            ]
