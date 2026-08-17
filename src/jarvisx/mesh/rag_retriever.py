"""Jarvis X: Semantic RAG Retrieval Tester & Similarity Engine.

Queries the local ChromaDB vector store on NANI to fetch top-k relevant knowledge chunks.
"""

from __future__ import annotations
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from typing import List, Dict, Any, Optional

import chromadb
import ollama

DEFAULT_DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "mxbai-embed-large"


class RAGRetriever:
    """Retrieves semantically relevant document chunks from ChromaDB."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH, embedding_model: str = EMBEDDING_MODEL):
        self.db_path = os.path.abspath(db_path)
        self.embedding_model = embedding_model
        self.client = chromadb.PersistentClient(path=self.db_path)
        try:
            self.collection = self.client.get_collection(name="jarvis_knowledge_base")
        except Exception:
            self.collection = None

    def is_ready(self) -> bool:
        return self.collection is not None and self.collection.count() > 0

    def query(self, search_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Query the vector database for the top-k most relevant matches."""
        if not self.is_ready():
            return []

        try:
            embed_res = ollama.embed(model=self.embedding_model, input=search_text)
            embeddings = embed_res.get("embeddings")
        except Exception:
            embeddings = None

        if embeddings:
            results = self.collection.query(
                query_embeddings=embeddings,
                n_results=top_k
            )
        else:
            results = self.collection.query(
                query_texts=[search_text],
                n_results=top_k
            )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        matches = []
        for idx in range(len(documents)):
            dist = distances[idx] if idx < len(distances) else 0.0
            meta = metadatas[idx] if idx < len(metadatas) else {}
            doc = documents[idx]
            matches.append({
                "rank": idx + 1,
                "distance": dist,
                "source": meta.get("source", "unknown"),
                "chunk_idx": meta.get("chunk_idx", 0),
                "content": doc
            })
        return matches

    def interactive_cli(self):
        """Run interactive search terminal."""
        if not self.is_ready():
            print(f"[-] Knowledge base not found or empty at '{self.db_path}'.")
            print("    Run 'python src/jarvisx/mesh/rag_ingestor.py' first.")
            return

        print("\n==================================================")
        print("  🔍 JARVIS X: KNOWLEDGE BASE QUERY TERMINAL")
        print("==================================================")
        print(f"  Connected to: {self.db_path} ({self.collection.count():,} chunks)")
        print("  Type 'exit' or 'quit' to exit.\n")

        while True:
            try:
                user_query = input("[?] Enter search query: ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if user_query.lower() in ["exit", "quit", "q"]:
                break
            if not user_query:
                continue

            matches = self.query(user_query, top_k=3)
            if not matches:
                print("[-] No matching knowledge chunks found.")
                continue

            for m in matches:
                print(f"\n--- Match {m['rank']} (Similarity Dist: {m['distance']:.4f}) | Source: {m['source']} ---")
                print(m["content"][:400] + ("..." if len(m["content"]) > 400 else ""))
                print("-" * 60)


if __name__ == "__main__":
    retriever = RAGRetriever()
    retriever.interactive_cli()
