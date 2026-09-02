"""Jarvis X: High-Speed Batch Knowledge Ingestion Engine.

Gathers all project code, architecture, training CoT examples, cluster config,
and user documents, chunking and ingesting into ChromaDB in bulk batches.
"""

from __future__ import annotations
import os
import sys
import glob
import json
from pathlib import Path
from typing import List, Dict, Any

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import chromadb
from jarvisx.mesh.rag_retriever import DEFAULT_DB_PATH, RAGRetriever


def build_knowledge_payload() -> List[Dict[str, Any]]:
    """Gathers all knowledge sources and generates chunked records."""
    records = []

    # 1. Core Persona & Mesh Topology
    core_facts = [
        ("core_identity", "User Profile: Charan is the creator, architect, and sovereign commander of Jarvis X. He uses Windows 11 on the NANI master laptop with Intel Iris Xe graphics."),
        ("core_topology", "Cluster Architecture: Jarvis X is a distributed AI mesh network operating over a private Tailscale VPN. Master node (NANI) runs at 100.105.164.83, coordinating STT/TTS, RAG, and tool execution."),
        ("core_workers", "Worker Nodes: Worker 1 (RTX 4050, tuf-a16 at 100.77.90.36) for code generation; Worker 3 (RTX 5050, laptop-lafr0e5l at 100.81.36.31) for heavy deep reasoning (deepseek-r1:14b); Worker 4 (ASUS TUF RTX 3050 16GB) for auxiliary compute; Worker 5 (Blackwell Beast RTX 5060 GDDR7) for ultra-fast deep reasoning and math."),
        ("core_protocol", "Communication Protocols: Health probing occurs via HTTP GET /api/tags on port 11434 with a 0.8s timeout. Auto-failover routes requests to local Ollama if remote GPU nodes sleep."),
        ("core_voice", "Voice Engine: SAPI SpVoice via win32com with pythoncom.CoInitialize() multi-threaded COM initialization, backed by PowerShell System.Speech synthesizer fallback. STT uses Google Speech Recognition with dynamic ambient noise adjustment."),
        ("core_security", "Security & Tools: ProductionSafetyGate enforces CONFIRM level for sensitive actions (file deletion, execution, system settings). Read/Write operations are sandboxed.")
    ]
    for tag, fact in core_facts:
        records.append({"source": tag, "content": fact})

    # 2. Chain-of-Thought Training Dataset
    dataset_file = Path("./jarvis_fine_tune_dataset.jsonl")
    if dataset_file.exists():
        with open(dataset_file, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f):
                if line.strip():
                    try:
                        obj = json.loads(line)
                        text = f"Instruction: {obj.get('instruction', '')}\nReasoning: {obj.get('thought', '')}\nResponse: {obj.get('output', '')}"
                        records.append({"source": f"training_cot_{idx}", "content": text})
                    except Exception:
                        pass

    # 3. Key Source Code Modules (Kernels, Mesh, Orchestration, Tools)
    src_paths = [
        "./src/jarvisx/mesh/mesh_router.py",
        "./src/jarvisx/mesh/rag_retriever.py",
        "./src/jarvisx/automation/dynamic_orchestrator.py",
        "./src/jarvisx/tools/tool_executor.py",
        "./src/jarvisx/tools/builtin_tools.py",
        "./src/jarvisx/interface/voice_duplex_engine.py",
        "./src/jarvisx/runtime/tray_daemon.py",
        "./src/jarvisx/main.py",
        "./Jarvis.Modelfile",
        "./README.md"
    ]
    for sp in src_paths:
        p = Path(sp)
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                # Chunk into 600-char segments
                for c_idx in range(0, max(1, len(content)), 600):
                    chunk = content[c_idx:c_idx + 600].strip()
                    if len(chunk) > 40:
                        records.append({"source": f"code_{p.name}_{c_idx}", "content": f"File: {p.name}\n{chunk}"})
            except Exception:
                pass

    # 4. User Documents (.txt / .md)
    user_docs_dir = Path.home() / "Documents"
    if user_docs_dir.exists():
        for ext in ("*.txt", "*.md"):
            for doc in glob.glob(str(user_docs_dir / ext)):
                try:
                    if os.path.getsize(doc) < 200_000:
                        with open(doc, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        if len(content.strip()) > 30:
                            for c_idx in range(0, len(content), 600):
                                chunk = content[c_idx:c_idx + 600].strip()
                                if len(chunk) > 40:
                                    records.append({"source": f"user_doc_{Path(doc).name}", "content": chunk})
                except Exception:
                    pass

    return records


def ingest_batch():
    print("========================================================", flush=True)
    print("  [*] JARVIS X: FAST BATCH KNOWLEDGE INGESTION", flush=True)
    print("========================================================\n", flush=True)

    records = build_knowledge_payload()
    print(f"[1/3] Extracted {len(records)} knowledge chunks across codebase & docs.", flush=True)

    # Connect to ChromaDB
    db_path = os.path.abspath(DEFAULT_DB_PATH)
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="jarvis_knowledge_base")

    existing_count = collection.count()
    print(f"[2/3] Existing ChromaDB collection count: {existing_count}", flush=True)

    # Ingest in chunks of 50
    batch_size = 50
    total_added = 0

    print("[3/3] Vectorizing and storing chunks into ChromaDB...", flush=True)
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        docs = [r["content"] for r in batch]
        metas = [{"source": r["source"], "idx": idx} for idx, r in enumerate(batch)]
        ids = [f"doc_{existing_count + total_added + idx}" for idx in range(len(batch))]

        collection.add(documents=docs, metadatas=metas, ids=ids)
        total_added += len(batch)
        print(f"      [+] Ingested {total_added}/{len(records)} chunks...", flush=True)

    new_total = collection.count()
    print("\n========================================================", flush=True)
    print(f"  [SUCCESS] All data fed into Jarvis X Memory!", flush=True)
    print(f"  Total Vector Knowledge Chunks: {new_total}", flush=True)
    print("========================================================\n", flush=True)

    # Verification query
    retriever = RAGRetriever()
    print("[*] Testing Live Memory Retrieval ('Who is Charan and what is NANI?')...", flush=True)
    results = retriever.query("Who is Charan and what is NANI", top_k=2)
    for idx, r in enumerate(results, 1):
        print(f"    Match #{idx} [Score: {r['score']}] Source: {r['source']}", flush=True)
        print(f"    {r['content'][:140]}...\n", flush=True)


if __name__ == "__main__":
    ingest_batch()
