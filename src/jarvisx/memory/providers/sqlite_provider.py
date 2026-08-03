"""
SQLite Long-Term Memory Provider for Cognitive Memory.
Real SQLite persistence with TF-IDF vector similarity search for decisions,
projects, preferences, goals, mistakes, and lessons learned.
"""
from __future__ import annotations
import json
import math
import re
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvisx.memory.providers.memory_provider import MemoryProvider


class SQLiteMemoryProvider(MemoryProvider):
    """
    Real persistent SQLite memory backend.
    Stores memories in `var/db/memory.db` with term-frequency cosine similarity search.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "var/db/memory.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    context_json TEXT NOT NULL,
                    text_corpus TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_cat ON memories(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
            conn.commit()

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r'\w+', text)]

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        tf: Dict[str, float] = {}
        if not tokens:
            return tf
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0
        n = float(len(tokens))
        for t in tf:
            tf[t] /= n
        return tf

    def _cosine_sim(self, tf1: Dict[str, float], tf2: Dict[str, float]) -> float:
        dot = sum(tf1[k] * tf2.get(k, 0.0) for k in tf1 if k in tf2)
        norm1 = math.sqrt(sum(v * v for v in tf1.values()))
        norm2 = math.sqrt(sum(v * v for v in tf2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    async def save(self, key: str, value: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> bool:
        category = str(value.get("type", "general"))
        val_str = json.dumps(value)
        ctx_str = json.dumps(context or {})
        corpus = f"{key} {category} {val_str} {ctx_str}"
        now = time.time()

        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories (id, category, key, value_json, context_json, text_corpus, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (key, category, key, val_str, ctx_str, corpus, now))
            conn.commit()
        return True

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        query_tf = self._compute_tf(query_tokens)

        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM memories").fetchall()

        scored = []
        for r in rows:
            doc_tokens = self._tokenize(r["text_corpus"])
            doc_tf = self._compute_tf(doc_tokens)
            sim = self._cosine_sim(query_tf, doc_tf)
            
            # Simple substring match boost
            if query.lower() in r["text_corpus"].lower():
                sim += 0.5

            if sim > 0.05:
                val = json.loads(r["value_json"])
                ctx = json.loads(r["context_json"])
                scored.append((sim, {
                    "key": r["id"],
                    "data": val,
                    "meta": ctx,
                    "score": round(sim, 3),
                    "created_at": r["created_at"]
                }))

        scored.sort(key=lambda x: (x[0], x[1]["created_at"]), reverse=True)
        return [item[1] for item in scored[:limit]]

    async def delete(self, key: str) -> bool:
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0

    async def sync(self, node_id: str, diff: Dict[str, Any]) -> bool:
        for k, v in diff.items():
            await self.save(k, v, {"synced_from": node_id})
        return True
