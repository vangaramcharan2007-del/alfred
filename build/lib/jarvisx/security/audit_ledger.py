"""
Cryptographic Tamper-Evident Audit Ledger for Jarvis X.
Adapted and refined from multi-agent trust layer patterns (awesome-llm-apps / trust-gated systems).

Features:
- Zero external cryptography dependencies (pure hashlib SHA-256 + json).
- Hash-chained event log: Each entry contains sha256(seq + timestamp + agent + action + input_hash + output_hash + prev_hash).
- Tamper detection: verify_chain() detects any retroactive payload modification in O(N).
- SQLite-backed transactional append.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


GENESIS_HASH = "0" * 64


@dataclass
class AuditEntry:
    sequence: int
    timestamp: float
    agent_id: str
    action: str
    input_hash: str
    output_hash: str
    status: str
    prev_hash: str
    current_hash: str
    metadata: Dict[str, Any]


class CryptographicAuditLedger:
    """Manages an immutable, hash-chained ledger of all autonomous actions."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            self.db_path = Path("var/db/audit_ledger.db")
        else:
            self.db_path = Path(db_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_chain (
                    sequence INTEGER PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    agent_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    input_hash TEXT NOT NULL,
                    output_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    current_hash TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def _compute_sha256(data: Any) -> str:
        """Compute deterministic SHA-256 hash of arbitrary data."""
        if isinstance(data, (dict, list)):
            serialized = json.dumps(data, sort_keys=True, default=str)
        else:
            serialized = str(data)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _compute_entry_hash(
        sequence: int,
        timestamp: float,
        agent_id: str,
        action: str,
        input_hash: str,
        output_hash: str,
        status: str,
        prev_hash: str,
    ) -> str:
        payload = f"{sequence}|{timestamp:.4f}|{agent_id}|{action}|{input_hash}|{output_hash}|{status}|{prev_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get_latest_entry(self) -> Optional[AuditEntry]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM audit_chain ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            if not row:
                return None
            return AuditEntry(
                sequence=row["sequence"],
                timestamp=row["timestamp"],
                agent_id=row["agent_id"],
                action=row["action"],
                input_hash=row["input_hash"],
                output_hash=row["output_hash"],
                status=row["status"],
                prev_hash=row["prev_hash"],
                current_hash=row["current_hash"],
                metadata=json.loads(row["metadata_json"]),
            )

    def record_action(
        self,
        agent_id: str,
        action: str,
        input_payload: Any,
        output_payload: Any,
        status: str = "SUCCESS",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """Record an action into the cryptographic hash chain."""
        latest = self.get_latest_entry()
        sequence = (latest.sequence + 1) if latest else 0
        prev_hash = latest.current_hash if latest else GENESIS_HASH
        timestamp = time.time()

        in_hash = self._compute_sha256(input_payload)
        out_hash = self._compute_sha256(output_payload)

        current_hash = self._compute_entry_hash(
            sequence=sequence,
            timestamp=timestamp,
            agent_id=agent_id,
            action=action,
            input_hash=in_hash,
            output_hash=out_hash,
            status=status,
            prev_hash=prev_hash,
        )

        meta = metadata or {}
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO audit_chain (
                    sequence, timestamp, agent_id, action, input_hash,
                    output_hash, status, prev_hash, current_hash, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sequence,
                    timestamp,
                    agent_id,
                    action,
                    in_hash,
                    out_hash,
                    status,
                    prev_hash,
                    current_hash,
                    json.dumps(meta),
                ),
            )
            conn.commit()

        return AuditEntry(
            sequence=sequence,
            timestamp=timestamp,
            agent_id=agent_id,
            action=action,
            input_hash=in_hash,
            output_hash=out_hash,
            status=status,
            prev_hash=prev_hash,
            current_hash=current_hash,
            metadata=meta,
        )

    def verify_integrity(self) -> Dict[str, Any]:
        """Verifies the entire cryptographic hash chain from Genesis to head."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM audit_chain ORDER BY sequence ASC").fetchall()

        if not rows:
            return {"valid": True, "total_records": 0, "status": "EMPTY_CHAIN"}

        expected_prev_hash = GENESIS_HASH
        for row in rows:
            seq = row["sequence"]
            prev_h = row["prev_hash"]

            if prev_h != expected_prev_hash:
                return {
                    "valid": False,
                    "tamper_detected_at_seq": seq,
                    "reason": f"Broken hash linkage: expected {expected_prev_hash}, found {prev_h}",
                }

            computed_hash = self._compute_entry_hash(
                sequence=seq,
                timestamp=row["timestamp"],
                agent_id=row["agent_id"],
                action=row["action"],
                input_hash=row["input_hash"],
                output_hash=row["output_hash"],
                status=row["status"],
                prev_hash=prev_h,
            )

            if computed_hash != row["current_hash"]:
                return {
                    "valid": False,
                    "tamper_detected_at_seq": seq,
                    "reason": f"Payload hash mismatch: recorded {row['current_hash']}, computed {computed_hash}",
                }

            expected_prev_hash = row["current_hash"]

        return {
            "valid": True,
            "total_records": len(rows),
            "head_hash": expected_prev_hash,
            "status": "HEALTHY_TAMPER_EVIDENT",
        }
