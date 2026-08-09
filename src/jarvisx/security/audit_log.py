"""Cryptographic SHA-256 Hash-Chained Audit Trail for Phase 99."""

from __future__ import annotations
import hashlib
import time
import uuid
from typing import Dict, List, Optional
from jarvisx.security.models import AuditEntry
from jarvisx.security.security_memory import SecurityMemory


class AuditLogger:
    """Tamper-proof append-only audit trail linking each log entry with the SHA-256 hash of its predecessor."""

    def __init__(self, memory: Optional[SecurityMemory] = None):
        self.memory = memory or SecurityMemory()

    def _compute_entry_hash(self, entry_id: str, ts: float, actor: str, action: str, risk: int, decision: str, prev_hash: str) -> str:
        payload = f"{entry_id}|{ts}|{actor}|{action}|{risk}|{decision}|{prev_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def log_event(self, actor: str, action: str, risk_score: int, decision: str) -> AuditEntry:
        """Append an audit entry linked cryptographically to the preceding entry."""
        entries = self.memory.list_audit_entries()
        prev_hash = entries[-1].current_hash if entries else ("0" * 64)

        entry_id = f"audit_{str(uuid.uuid4())[:8]}"
        now = time.time()
        curr_hash = self._compute_entry_hash(entry_id, now, actor, action, risk_score, decision, prev_hash)

        entry = AuditEntry(
            id=entry_id,
            timestamp=now,
            actor=actor,
            action=action,
            risk_score=risk_score,
            decision=decision,
            previous_hash=prev_hash,
            current_hash=curr_hash
        )
        self.memory.append_audit_entry(entry)
        return entry

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify the cryptographic integrity of the entire audit chain."""
        entries = self.memory.list_audit_entries()
        if not entries:
            return {"valid": True, "total_entries": 0, "status": "EMPTY_CHAIN"}

        expected_prev = "0" * 64
        for idx, e in enumerate(entries):
            if e.previous_hash != expected_prev:
                return {
                    "valid": False,
                    "tampered_index": idx,
                    "entry_id": e.id,
                    "reason": "Previous hash mismatch (tampering detected)"
                }

            recomputed = self._compute_entry_hash(e.id, e.timestamp, e.actor, e.action, e.risk_score, e.decision, e.previous_hash)
            if recomputed != e.current_hash:
                return {
                    "valid": False,
                    "tampered_index": idx,
                    "entry_id": e.id,
                    "reason": "Current hash mismatch (tampering detected)"
                }

            expected_prev = e.current_hash

        return {"valid": True, "total_entries": len(entries), "status": "CHAIN_VERIFIED"}
