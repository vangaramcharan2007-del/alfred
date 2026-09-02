"""Persistent SQLite Metadata Store for Jarvis X Knowledge Subsystem."""

from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from jarvisx.knowledge.models import (
    DocumentMetadata,
    KnowledgeChunk,
    KnowledgeSensitivity,
    VaultCategory,
)


class KnowledgeMetadataIndex:
    """Dedicated SQLite Store for document provenance, chunk metadata, tags, and security levels."""

    def __init__(self, db_path: str = "var/db/knowledge.db"):
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
            cur.execute("INSERT OR IGNORE INTO schema_meta (version, upgraded_at) VALUES ('v1.1', ?)", (time.time(),))

            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    source_file TEXT PRIMARY KEY,
                    source_type TEXT,
                    category TEXT,
                    sensitivity TEXT,
                    content_hash TEXT,
                    title TEXT,
                    tags_json TEXT,
                    wikilinks_json TEXT,
                    frontmatter_json TEXT,
                    file_size_bytes INTEGER,
                    created_at REAL,
                    last_modified REAL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    source_file TEXT,
                    chunk_index INTEGER,
                    content TEXT,
                    heading_path TEXT,
                    content_hash TEXT,
                    tags_json TEXT,
                    wikilinks_json TEXT,
                    sensitivity TEXT,
                    category TEXT,
                    created_at REAL,
                    FOREIGN KEY (source_file) REFERENCES documents(source_file) ON DELETE CASCADE
                )
            """)

            # Indexing for rapid lookup
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_file)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_category ON chunks(category)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_sensitivity ON chunks(sensitivity)")
            conn.commit()

    def get_document(self, source_file: str) -> Optional[DocumentMetadata]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT source_file, source_type, category, sensitivity, content_hash,
                       title, tags_json, wikilinks_json, frontmatter_json,
                       file_size_bytes, created_at, last_modified
                FROM documents WHERE source_file = ?
            """, (source_file,))
            row = cur.fetchone()
            if not row:
                return None
            return DocumentMetadata(
                source_file=row[0],
                source_type=row[1],
                category=VaultCategory(row[2]) if row[2] in [c.value for c in VaultCategory] else VaultCategory.GENERAL,
                sensitivity=KnowledgeSensitivity(row[3]) if row[3] in [s.value for s in KnowledgeSensitivity] else KnowledgeSensitivity.INTERNAL,
                content_hash=row[4],
                title=row[5],
                tags=json.loads(row[6]) if row[6] else [],
                wikilinks=json.loads(row[7]) if row[7] else [],
                frontmatter=json.loads(row[8]) if row[8] else {},
                file_size_bytes=row[9],
                created_at=row[10],
                last_modified=row[11],
            )

    def save_document(self, doc: DocumentMetadata, chunks: List[KnowledgeChunk]) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            # 1. Upsert document record
            cur.execute("""
                INSERT OR REPLACE INTO documents (
                    source_file, source_type, category, sensitivity, content_hash,
                    title, tags_json, wikilinks_json, frontmatter_json,
                    file_size_bytes, created_at, last_modified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.source_file,
                doc.source_type,
                doc.category.value if isinstance(doc.category, VaultCategory) else str(doc.category),
                doc.sensitivity.value if isinstance(doc.sensitivity, KnowledgeSensitivity) else str(doc.sensitivity),
                doc.content_hash,
                doc.title,
                json.dumps(doc.tags),
                json.dumps(doc.wikilinks),
                json.dumps(doc.frontmatter),
                doc.file_size_bytes,
                doc.created_at,
                doc.last_modified,
            ))

            # 2. Delete old chunks for this document
            cur.execute("DELETE FROM chunks WHERE source_file = ?", (doc.source_file,))

            # 3. Insert new chunks
            for c in chunks:
                cur.execute("""
                    INSERT INTO chunks (
                        id, source_file, chunk_index, content, heading_path,
                        content_hash, tags_json, wikilinks_json, sensitivity, category, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    c.id,
                    c.source_file,
                    c.chunk_index,
                    c.content,
                    c.heading_path,
                    c.content_hash,
                    json.dumps(c.tags),
                    json.dumps(c.wikilinks),
                    c.sensitivity.value if isinstance(c.sensitivity, KnowledgeSensitivity) else str(c.sensitivity),
                    c.category.value if isinstance(c.category, VaultCategory) else str(c.category),
                    c.created_at,
                ))
            conn.commit()

    def delete_document(self, source_file: str) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM chunks WHERE source_file = ?", (source_file,))
            cur.execute("DELETE FROM documents WHERE source_file = ?", (source_file,))
            conn.commit()

    def list_all_documents(self) -> List[DocumentMetadata]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT source_file, source_type, category, sensitivity, content_hash,
                       title, tags_json, wikilinks_json, frontmatter_json,
                       file_size_bytes, created_at, last_modified
                FROM documents ORDER BY last_modified DESC
            """)
            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append(DocumentMetadata(
                    source_file=row[0],
                    source_type=row[1],
                    category=VaultCategory(row[2]) if row[2] in [c.value for c in VaultCategory] else VaultCategory.GENERAL,
                    sensitivity=KnowledgeSensitivity(row[3]) if row[3] in [s.value for s in KnowledgeSensitivity] else KnowledgeSensitivity.INTERNAL,
                    content_hash=row[4],
                    title=row[5],
                    tags=json.loads(row[6]) if row[6] else [],
                    wikilinks=json.loads(row[7]) if row[7] else [],
                    frontmatter=json.loads(row[8]) if row[8] else {},
                    file_size_bytes=row[9],
                    created_at=row[10],
                    last_modified=row[11],
                ))
            return results

    def list_all_chunks(self, max_sensitivity: Optional[KnowledgeSensitivity] = None) -> List[KnowledgeChunk]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, source_file, chunk_index, content, heading_path,
                       content_hash, tags_json, wikilinks_json, sensitivity, category, created_at
                FROM chunks
            """)
            rows = cur.fetchall()
            results = []
            for row in rows:
                sens = KnowledgeSensitivity(row[8]) if row[8] in [s.value for s in KnowledgeSensitivity] else KnowledgeSensitivity.INTERNAL
                results.append(KnowledgeChunk(
                    id=row[0],
                    source_file=row[1],
                    chunk_index=row[2],
                    content=row[3],
                    heading_path=row[4],
                    content_hash=row[5],
                    tags=json.loads(row[6]) if row[6] else [],
                    wikilinks=json.loads(row[7]) if row[7] else [],
                    sensitivity=sens,
                    category=VaultCategory(row[9]) if row[9] in [c.value for c in VaultCategory] else VaultCategory.GENERAL,
                    created_at=row[10],
                ))
            return results

    def get_stats(self) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM documents")
            doc_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM chunks")
            chunk_count = cur.fetchone()[0]
            cur.execute("SELECT category, COUNT(*) FROM documents GROUP BY category")
            cats = {row[0]: row[1] for row in cur.fetchall()}
            return {
                "total_documents": doc_count,
                "total_chunks": chunk_count,
                "categories": cats,
            }
