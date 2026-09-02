import os
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple

try:
    import ollama
except ImportError:
    ollama = None

class VectorMemory:
    """
    Long-Term Semantic Vector Memory for Jarvis X using Ollama local embeddings.
    Allows Jarvis X to recall past conversations, facts, and code snippets.
    """
    
    def __init__(self, db_name: str = "long_term_memory"):
        self.db_path = Path(os.getcwd()) / "var" / "db" / f"{db_name}.json"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.model = "nomic-embed-text"
        self.records: List[Dict[str, Any]] = self._load_db()

    def _load_db(self) -> List[Dict[str, Any]]:
        if self.db_path.exists():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_db(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2)

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(v1)):
            x = v1[i]
            y = v2[i]
            sumxx += x*x
            sumyy += y*y
            sumxy += x*y
        return sumxy / math.sqrt(sumxx * sumyy) if (sumxx * sumyy) > 0 else 0

    def add_memory(self, text: str, metadata: Dict[str, Any] = None):
        """Embeds and saves a text snippet into long-term memory."""
        if not ollama:
            return False
            
        try:
            res = ollama.embeddings(model=self.model, prompt=text)
            embedding = res.get("embedding")
            if embedding:
                self.records.append({
                    "text": text,
                    "embedding": embedding,
                    "metadata": metadata or {}
                })
                self._save_db()
                return True
        except Exception as e:
            print(f"[VectorMemory] Failed to embed: {e}")
        return False

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Searches memory for the most semantically similar text."""
        if not ollama or not self.records:
            return []
            
        try:
            res = ollama.embeddings(model=self.model, prompt=query)
            query_embedding = res.get("embedding")
            if not query_embedding:
                return []
                
            results = []
            for record in self.records:
                sim = self._cosine_similarity(query_embedding, record["embedding"])
                results.append((sim, record))
                
            # Sort by similarity descending
            results.sort(key=lambda x: x[0], reverse=True)
            
            # Return top_k without the heavy embedding array
            top_records = []
            for sim, record in results[:top_k]:
                # Only return hits with decent confidence (> 0.5)
                if sim > 0.5:
                    top_records.append({
                        "similarity": round(sim, 3),
                        "text": record["text"],
                        "metadata": record["metadata"]
                    })
            return top_records
        except Exception as e:
            print(f"[VectorMemory] Search failed: {e}")
            return []
