"""Jarvis X: High-Performance RAG Ingestion Pipeline.

Parses PDFs, Code, Markdown, and Syllabus notes, generates semantic embeddings,
and stores them persistently in a local ChromaDB vector store on the Master Control Plane (NANI).
"""

from __future__ import annotations
import os
import sys
import glob

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import chromadb
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
import ollama
from pypdf import PdfReader

# Default Paths & Configuration
DEFAULT_DATA_DIR = "./jarvis_data_dump"
DEFAULT_DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "mxbai-embed-large"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 20


class RAGIngestor:
    """Ingests multi-format documents into ChromaDB with semantic chunking."""

    def __init__(
        self,
        data_dir: str = DEFAULT_DATA_DIR,
        db_path: str = DEFAULT_DB_PATH,
        embedding_model: str = EMBEDDING_MODEL
    ):
        self.data_dir = os.path.abspath(data_dir)
        self.db_path = os.path.abspath(db_path)
        self.embedding_model = embedding_model
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(
            name="jarvis_knowledge_base",
            metadata={"description": "Central Jarvis X RAG Knowledge Base"}
        )

    def extract_text_from_pdf(self, filepath: str) -> str:
        """Extract text content from all pages of a PDF."""
        text_parts = []
        try:
            reader = PdfReader(filepath)
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {idx + 1} ---\n{page_text}")
        except Exception as e:
            print(f"  [!] Warning reading PDF '{filepath}': {e}")
        return "\n".join(text_parts)

    def extract_text_from_file(self, filepath: str) -> str:
        """Read standard markdown, source code, and text files."""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"  [!] Warning reading text file '{filepath}': {e}")
            return ""

    def chunk_text(self, text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split raw text into overlapping context windows."""
        if not text:
            return []
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + size, text_len)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end == text_len:
                break
            start += max(1, size - overlap)
        return chunks

    def _get_embeddings_batch(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Generate embeddings using Ollama or ChromaDB default fallback."""
        try:
            res = ollama.embed(model=self.embedding_model, input=texts)
            return res.get("embeddings")
        except Exception as e:
            print(f"  [!] Notice: Ollama embedding model '{self.embedding_model}' fallback: {e}")
            return None

    def ingest_directory(self) -> Dict[str, Any]:
        """Scan and ingest all documents in data_dir into ChromaDB."""
        print(f"\n========================================================")
        print(f"  🧠 JARVIS X: RAG VECTOR INGESTION PIPELINE")
        print(f"========================================================")
        print(f"  Data Dump Directory : {self.data_dir}")
        print(f"  ChromaDB Storage    : {self.db_path}")
        print(f"  Embedding Engine    : {self.embedding_model}")
        print(f"========================================================\n")

        files = glob.glob(os.path.join(self.data_dir, "**", "*.*"), recursive=True)
        supported_exts = {
            ".pdf", ".md", ".txt", ".py", ".java", ".cpp", ".c", ".h",
            ".js", ".ts", ".json", ".yaml", ".yml", ".html", ".sql"
        }

        target_files = [f for f in files if os.path.splitext(f)[1].lower() in supported_exts]
        if not target_files:
            print(f"[*] No supported documents found in '{self.data_dir}'.")
            print(f"    Please place PDFs, Code, or Notes in this directory and re-run.")
            return {"status": "empty", "files_processed": 0, "chunks_added": 0}

        total_chunks = 0
        files_processed = 0

        for filepath in target_files:
            rel_path = os.path.relpath(filepath, self.data_dir)
            ext = os.path.splitext(filepath)[1].lower()
            print(f"[*] Processing: {rel_path} ({ext})")

            content = (
                self.extract_text_from_pdf(filepath)
                if ext == ".pdf"
                else self.extract_text_from_file(filepath)
            )

            if not content.strip():
                print(f"    ⚠️ Skipping empty file.")
                continue

            chunks = self.chunk_text(content)
            if not chunks:
                continue

            file_base = os.path.basename(filepath)
            for i in range(0, len(chunks), BATCH_SIZE):
                batch = chunks[i : i + BATCH_SIZE]
                batch_ids = [f"{file_base}_c{j}_{os.urandom(2).hex()}" for j in range(i, i + len(batch))]
                batch_metas = [{"source": rel_path, "chunk_idx": j, "file_ext": ext} for j in range(i, i + len(batch))]

                embeddings = self._get_embeddings_batch(batch)
                if embeddings:
                    self.collection.add(
                        ids=batch_ids,
                        embeddings=embeddings,
                        documents=batch,
                        metadatas=batch_metas
                    )
                else:
                    # ChromaDB built-in default embedding
                    self.collection.add(
                        ids=batch_ids,
                        documents=batch,
                        metadatas=batch_metas
                    )

            total_chunks += len(chunks)
            files_processed += 1
            print(f"    ✅ Ingested {len(chunks)} chunks into vector store.")

        total_count = self.collection.count()
        print(f"\n========================================================")
        print(f"  ✅ INGESTION COMPLETE: {files_processed} files | {total_chunks} new chunks")
        print(f"  📚 Total Knowledge Base Vectors: {total_count:,} chunks")
        print(f"========================================================\n")

        return {
            "status": "success",
            "files_processed": files_processed,
            "chunks_added": total_chunks,
            "total_vectors": total_count
        }


if __name__ == "__main__":
    ingestor = RAGIngestor()
    ingestor.ingest_directory()
