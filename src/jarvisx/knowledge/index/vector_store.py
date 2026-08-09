"""Local Dense Vector Store for Jarvis X Knowledge Subsystem."""

from __future__ import annotations
import json
import math
import re
from pathlib import Path
from typing import Dict, List, Tuple
from jarvisx.knowledge.models import KnowledgeChunk


class LocalVectorStore:
    """Offline-First Dense Vector Store storing embedding vectors in var/knowledge/vectors/."""

    VECTOR_DIM = 128

    def __init__(self, index_path: str = "var/knowledge/vectors/vector_index.json"):
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.vectors: Dict[str, List[float]] = {}
        self.chunk_sources: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self.index_path.exists():
            try:
                data = json.loads(self.index_path.read_text(encoding="utf-8"))
                self.vectors = data.get("vectors", {})
                self.chunk_sources = data.get("chunk_sources", {})
            except Exception:
                self.vectors = {}
                self.chunk_sources = {}

    def _save(self) -> None:
        data = {
            "dim": self.VECTOR_DIM,
            "count": len(self.vectors),
            "vectors": self.vectors,
            "chunk_sources": self.chunk_sources,
        }
        self.index_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _embed(self, text: str) -> List[float]:
        """Produce a normalized 128-dimensional dense semantic embedding vector using trigram frequency hashing."""
        clean = re.sub(r"[^\w\s]", " ", text.lower())
        words = clean.split()
        vec = [0.0] * self.VECTOR_DIM

        # 1. Word token hashing
        for w in words:
            h = hash(w) % self.VECTOR_DIM
            vec[h] += 1.0

        # 2. Character trigrams for morphological and subword semantic capture
        for i in range(len(clean) - 2):
            tri = clean[i : i + 3]
            h = hash(tri) % self.VECTOR_DIM
            vec[h] += 0.5

        # 3. L2 Normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 1e-9:
            return [round(x / norm, 5) for x in vec]
        return vec

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        return max(0.0, min(1.0, dot))

    def index_chunk(self, chunk: KnowledgeChunk) -> None:
        """Embed and store chunk vector."""
        combined_text = f"{chunk.heading_path}\n{' '.join(chunk.tags)}\n{chunk.content}"
        vec = self._embed(combined_text)
        self.vectors[chunk.id] = vec
        self.chunk_sources[chunk.id] = chunk.source_file

    def index_chunks_batch(self, chunks: List[KnowledgeChunk]) -> None:
        for c in chunks:
            self.index_chunk(c)
        self._save()

    def remove_source(self, source_file: str) -> None:
        """Purge all chunk vectors originating from source_file."""
        to_delete = [cid for cid, src in self.chunk_sources.items() if src == source_file]
        for cid in to_delete:
            self.vectors.pop(cid, None)
            self.chunk_sources.pop(cid, None)
        self._save()

    def clear(self) -> None:
        self.vectors.clear()
        self.chunk_sources.clear()
        self._save()

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Search vector index for top_k most similar chunk IDs with cosine similarity scores."""
        if not self.vectors:
            return []

        q_vec = self._embed(query)
        scored: List[Tuple[str, float]] = []

        for cid, vec in self.vectors.items():
            sim = self._cosine_similarity(q_vec, vec)
            scored.append((cid, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
