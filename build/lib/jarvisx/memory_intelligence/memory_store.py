"""SQLite Storage Engine for Phase 103 Memory Intelligence."""

from __future__ import annotations
import json
from pathlib import Path
import sqlite3
import time
from typing import Any, Dict, List, Optional

from jarvisx.memory_intelligence.models import (
    MemoryProvenance,
    MemoryRecord,
    MemoryRelation,
    MemorySensitivity,
    MemorySource,
    MemoryType,
    RelationType,
)


class MemoryStore:
    """Persistent, thread-safe SQLite storage for cognitive memories and relations."""

    def __init__(self, db_path: str = "var/db/memory_intelligence.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance_score REAL NOT NULL,
                confidence REAL NOT NULL,
                sensitivity TEXT NOT NULL,
                source_type TEXT NOT NULL,
                evidence_text TEXT,
                source_ref TEXT,
                tags_json TEXT,
                created_at REAL NOT NULL,
                last_accessed_at REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                is_archived INTEGER DEFAULT 0,
                metadata_json TEXT
            );

            CREATE TABLE IF NOT EXISTS memory_relations (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at REAL NOT NULL,
                PRIMARY KEY (source_id, target_id, relation_type),
                FOREIGN KEY (source_id) REFERENCES memories(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES memories(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS memory_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT NOT NULL,
                user_accepted INTEGER,
                user_feedback TEXT,
                created_at REAL NOT NULL,
                FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_mem_type ON memories(memory_type);
            CREATE INDEX IF NOT EXISTS idx_mem_archived ON memories(is_archived);
            CREATE INDEX IF NOT EXISTS idx_mem_importance ON memories(importance_score DESC);
            """)

    def save_memory(self, record: MemoryRecord) -> None:
        """Insert or update a memory record."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memories (
                    id, memory_type, content, importance_score, confidence, sensitivity,
                    source_type, evidence_text, source_ref, tags_json, created_at,
                    last_accessed_at, access_count, is_archived, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.memory_type.value,
                    record.content,
                    record.importance_score,
                    record.confidence,
                    record.sensitivity.value,
                    record.provenance.source_type.value,
                    record.provenance.evidence_text,
                    record.provenance.source_ref,
                    json.dumps(record.tags),
                    record.created_at,
                    record.last_accessed_at,
                    record.access_count,
                    1 if record.is_archived else 0,
                    json.dumps(record.metadata),
                ),
            )

    def get_memory(self, memory_id: str) -> Optional[MemoryRecord]:
        """Fetch memory record by ID and update access tracking."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
            if not row:
                return None

            now = time.time()
            conn.execute(
                "UPDATE memories SET last_accessed_at = ?, access_count = access_count + 1 WHERE id = ?",
                (now, memory_id),
            )
            return self._row_to_record(row)

    def list_memories(
        self,
        memory_type: Optional[MemoryType] = None,
        include_archived: bool = False,
        limit: int = 100,
    ) -> List[MemoryRecord]:
        """List memories filtered by type and archival status."""
        query = "SELECT * FROM memories WHERE 1=1"
        params: List[Any] = []

        if not include_archived:
            query += " AND is_archived = 0"
        if memory_type:
            query += " AND memory_type = ?"
            params.append(memory_type.value)

        query += " ORDER BY importance_score DESC, created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
            return [self._row_to_record(r) for r in rows]

    def add_relation(self, relation: MemoryRelation) -> None:
        """Create a semantic link between two memories."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memory_relations (
                    source_id, target_id, relation_type, confidence, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    relation.source_id,
                    relation.target_id,
                    relation.relation_type.value,
                    relation.confidence,
                    relation.created_at,
                ),
            )

    def get_relations_for_memory(self, memory_id: str) -> List[MemoryRelation]:
        """Fetch all incoming and outgoing relations for a memory."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM memory_relations WHERE source_id = ? OR target_id = ?",
                (memory_id, memory_id),
            ).fetchall()
            return [
                MemoryRelation(
                    source_id=r["source_id"],
                    target_id=r["target_id"],
                    relation_type=RelationType(r["relation_type"]),
                    confidence=float(r["confidence"]),
                    created_at=float(r["created_at"]),
                )
                for r in rows
            ]

    def archive_memory(self, memory_id: str) -> bool:
        """Soft-archive a memory."""
        with self._get_connection() as conn:
            cur = conn.execute("UPDATE memories SET is_archived = 1 WHERE id = ?", (memory_id,))
            return cur.rowcount > 0

    def delete_memory(self, memory_id: str) -> bool:
        """Permanently delete a memory and its relations."""
        with self._get_connection() as conn:
            cur = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            return cur.rowcount > 0

    def count_memories(self) -> Dict[str, int]:
        """Return memory breakdown counts."""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories WHERE is_archived = 0").fetchone()[0]
            episodic = conn.execute("SELECT COUNT(*) FROM memories WHERE memory_type = 'EPISODIC' AND is_archived = 0").fetchone()[0]
            semantic = conn.execute("SELECT COUNT(*) FROM memories WHERE memory_type = 'SEMANTIC' AND is_archived = 0").fetchone()[0]
            procedural = conn.execute("SELECT COUNT(*) FROM memories WHERE memory_type = 'PROCEDURAL' AND is_archived = 0").fetchone()[0]
            archived = conn.execute("SELECT COUNT(*) FROM memories WHERE is_archived = 1").fetchone()[0]

            return {
                "total_active": total,
                "episodic": episodic,
                "semantic": semantic,
                "procedural": procedural,
                "archived": archived,
            }

    def _row_to_record(self, row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            id=row["id"],
            memory_type=MemoryType(row["memory_type"]),
            content=row["content"],
            importance_score=float(row["importance_score"]),
            confidence=float(row["confidence"]),
            sensitivity=MemorySensitivity(row["sensitivity"]),
            provenance=MemoryProvenance(
                source_type=MemorySource(row["source_type"]),
                evidence_text=row["evidence_text"] or "",
                source_ref=row["source_ref"] or "",
                timestamp=float(row["created_at"]),
            ),
            tags=json.loads(row["tags_json"] or "[]"),
            created_at=float(row["created_at"]),
            last_accessed_at=float(row["last_accessed_at"]),
            access_count=int(row["access_count"]),
            is_archived=bool(row["is_archived"]),
            metadata=json.loads(row["metadata_json"] or "{}"),
        )
