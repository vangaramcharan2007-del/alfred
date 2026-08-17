"""Jarvis X: Advanced Agentic RAG & Hybrid Retrieval Engine.

Features:
1. Hybrid Search: BM25 Lexical Keyword Ranking + Dense ChromaDB Vector Embeddings.
2. Reciprocal Rank Fusion (RRF): Optimal fusion of keyword & semantic rankings.
3. Corrective RAG (CRAG): Autonomous query reformulation and verification loop.
"""

from __future__ import annotations
import os
import sys
import math
import re
from typing import List, Dict, Any, Optional, Set
from collections import Counter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import chromadb
import ollama

DEFAULT_DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "mxbai-embed-large"


class BM25Ranker:
    """Zero-dependency BM25 Lexical Keyword Ranker for Code & Documentation."""

    def __init__(self, corpus: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.doc_len = [len(self._tokenize(doc)) for doc in corpus]
        self.avg_doc_len = sum(self.doc_len) / len(self.doc_len) if self.doc_len else 1.0
        self.doc_freqs: List[Counter] = [Counter(self._tokenize(doc)) for doc in corpus]
        self.idf = self._calc_idf()

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b\w+\b", text)]

    def _calc_idf(self) -> Dict[str, float]:
        idf = {}
        total_docs = len(self.corpus)
        df_counter: Counter = Counter()
        for df in self.doc_freqs:
            for term in df.keys():
                df_counter[term] += 1
        for term, freq in df_counter.items():
            idf[term] = math.log((total_docs - freq + 0.5) / (freq + 0.5) + 1.0)
        return idf

    def score(self, query: str) -> List[float]:
        q_tokens = self._tokenize(query)
        scores = []
        for idx, df in enumerate(self.doc_freqs):
            doc_l = self.doc_len[idx]
            score = 0.0
            for term in q_tokens:
                if term not in df:
                    continue
                tf = df[term]
                idf = self.idf.get(term, 0.0)
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_l / self.avg_doc_len))
                score += idf * (numerator / denominator)
            scores.append(score)
        return scores


class RAGRetriever:
    """Advanced Hybrid RAG Retriever with BM25 + Dense Vector + Corrective RAG (CRAG)."""

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

    def hybrid_search(self, query: str, top_k: int = 4, rrf_k: int = 60) -> List[Dict[str, Any]]:
        """Executes Hybrid Search combining Dense ChromaDB Embeddings with BM25 Lexical Ranking."""
        if not self.is_ready():
            return []

        # 1. Fetch Dense Vector Matches
        try:
            embed_res = ollama.embed(model=self.embedding_model, input=query)
            embeddings = embed_res.get("embeddings")
        except Exception:
            embeddings = None

        if embeddings:
            dense_res = self.collection.query(query_embeddings=embeddings, n_results=min(15, self.collection.count()))
        else:
            dense_res = self.collection.query(query_texts=[query], n_results=min(15, self.collection.count()))

        dense_docs = dense_res.get("documents", [[]])[0]
        dense_metas = dense_res.get("metadatas", [[]])[0]
        dense_ids = dense_res.get("ids", [[]])[0]

        # 2. Get All Documents for Lexical Scoring
        all_data = self.collection.get()
        all_docs = all_data.get("documents", [])
        all_metas = all_data.get("metadatas", [])
        all_ids = all_data.get("ids", [])

        if not all_docs:
            return []

        # 3. Compute BM25 Scores
        bm25 = BM25Ranker(all_docs)
        bm25_scores = bm25.score(query)
        bm25_sorted_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)

        # 4. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        doc_store: Dict[str, Dict[str, Any]] = {}

        # Dense ranking contribution
        for rank, doc_id in enumerate(dense_ids):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank + 1))
            doc_store[doc_id] = {
                "content": dense_docs[rank],
                "metadata": dense_metas[rank] if rank < len(dense_metas) else {}
            }

        # BM25 ranking contribution
        for rank, idx in enumerate(bm25_sorted_indices[:15]):
            doc_id = all_ids[idx]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank + 1))
            if doc_id not in doc_store:
                doc_store[doc_id] = {
                    "content": all_docs[idx],
                    "metadata": all_metas[idx] if idx < len(all_metas) else {}
                }

        # 5. Sort by final RRF Score
        fused_sorted = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        matches = []
        for rank, (doc_id, score) in enumerate(fused_sorted):
            data = doc_store[doc_id]
            meta = data["metadata"]
            matches.append({
                "rank": rank + 1,
                "score": round(score, 5),
                "source": meta.get("source", "unknown"),
                "chunk_idx": meta.get("chunk_idx", 0),
                "content": data["content"]
            })

        return matches

    def corrective_rag_query(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Corrective RAG (CRAG) loop with autonomous query reformulation."""
        matches = self.hybrid_search(query, top_k=top_k)
        
        # Self-correction check: If top match score is very low, formulate query keywords
        if not matches or matches[0].get("score", 0) < 0.02:
            keywords = [w for w in re.findall(r"\b\w{4,}\b", query) if w.lower() not in ["what", "where", "how", "when", "explain", "describe"]]
            if keywords:
                refined_query = " ".join(keywords)
                refined_matches = self.hybrid_search(refined_query, top_k=top_k)
                if refined_matches:
                    return refined_matches

        return matches

    def query(self, search_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Standard query interface pointing to advanced Corrective RAG."""
        return self.corrective_rag_query(search_text, top_k=top_k)


def get_rag_retriever() -> RAGRetriever:
    return RAGRetriever()


if __name__ == "__main__":
    retriever = RAGRetriever()
    print("Testing Hybrid Search (BM25 + ChromaDB Vector + RRF):")
    res = retriever.corrective_rag_query("PersonalOSKernel tool executor permissions", top_k=2)
    for r in res:
        print(f"Rank {r['rank']} [Score: {r['score']}] Source: {r['source']}")
        print(f"{r['content'][:150]}...\n")
