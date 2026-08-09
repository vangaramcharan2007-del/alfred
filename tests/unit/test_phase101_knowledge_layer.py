"""Unit Tests for Phase 101 / v1.1 Knowledge Acquisition & Obsidian Vault Layer."""

from pathlib import Path
import pytest

from jarvisx.knowledge.context_builder import KnowledgeContextComposer
from jarvisx.knowledge.index.knowledge_index import KnowledgeMetadataIndex
from jarvisx.knowledge.index.vector_store import LocalVectorStore
from jarvisx.knowledge.ingestion.document_loader import DocumentLoader
from jarvisx.knowledge.ingestion.markdown_parser import ObsidianMarkdownParser
from jarvisx.knowledge.knowledge_engine import KnowledgeEngine
from jarvisx.knowledge.models import (
    KnowledgeChunk,
    KnowledgeSensitivity,
    VaultCategory,
)
from jarvisx.knowledge.vault.vault_manager import ObsidianVaultManager


@pytest.fixture
def temp_vault_env(tmp_path):
    vault_dir = tmp_path / "vault"
    db_file = str(tmp_path / "knowledge.db")
    vec_file = str(tmp_path / "vectors.json")
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir, db_file, vec_file


def test_obsidian_vault_scaffolding_and_categories(temp_vault_env):
    vault_dir, _, _ = temp_vault_env
    mgr = ObsidianVaultManager(str(vault_dir))
    res = mgr.initialize_vault()

    assert res["status"] == "INITIALIZED"
    assert (vault_dir / "00_Inbox").exists()
    assert (vault_dir / "01_Goals").exists()
    assert (vault_dir / "02_Learning").exists()
    assert (vault_dir / "03_Projects").exists()
    assert (vault_dir / "04_References").exists()
    assert (vault_dir / "05_Memory").exists()
    assert (vault_dir / "02_Learning/README.md").exists()

    cat, sens = mgr.infer_category_and_sensitivity(vault_dir / "05_Memory/mindset.md")
    assert cat == VaultCategory.MEMORY
    assert sens == KnowledgeSensitivity.SENSITIVE_MEMORY


def test_markdown_parser_frontmatter_tags_and_wikilinks():
    parser = ObsidianMarkdownParser()
    sample_md = """---
title: Binary Search Trees
category: 02_Learning
tags: [dsa, trees, algorithms]
importance: high
---

# Binary Search Trees

A binary search tree maintains the invariant: `left < root < right`.
Refer to [[Heap Data Structure]] and #complexity analysis.

## Traversals
In-order traversal visits nodes in sorted order.
See [[Graph Algorithms]] for details.

### Implementation
```python
def inorder(root):
    return inorder(root.left) + [root.val] + inorder(root.right) if root else []
```
"""
    meta, chunks = parser.parse_document(
        raw_text=sample_md,
        source_file="02_Learning/DSA/BST.md",
        category=VaultCategory.LEARNING,
        sensitivity=KnowledgeSensitivity.INTERNAL,
    )

    assert meta["title"] == "Binary Search Trees"
    assert "dsa" in meta["tags"]
    assert "complexity" in meta["tags"]
    assert "Heap Data Structure" in meta["wikilinks"]
    assert "Graph Algorithms" in meta["wikilinks"]
    assert len(chunks) >= 3
    assert any("Traversals" in c.heading_path for c in chunks)


def test_document_loader_multi_format(temp_vault_env):
    vault_dir, _, _ = temp_vault_env
    loader = DocumentLoader()

    # 1. Markdown file
    md_path = vault_dir / "note.md"
    md_path.write_text("# Test Note\nContent goes here.", encoding="utf-8")
    doc_meta, chunks = loader.load_file(md_path)
    assert doc_meta.source_type == "markdown"
    assert len(chunks) >= 1

    # 2. Python code file
    py_path = vault_dir / "app.py"
    py_path.write_text("def hello():\n    print('Hello World')", encoding="utf-8")
    py_meta, py_chunks = loader.load_file(py_path)
    assert py_meta.source_type == "text"
    assert len(py_chunks) >= 1


def test_knowledge_metadata_and_vector_store_separation(temp_vault_env):
    vault_dir, db_file, vec_file = temp_vault_env
    meta_idx = KnowledgeMetadataIndex(db_file)
    vec_store = LocalVectorStore(vec_file)

    chunk = KnowledgeChunk(
        id="chunk_01",
        source_file="02_Learning/DSA/trees.md",
        chunk_index=0,
        content="Hierarchical binary search tree algorithms.",
        heading_path="# DSA > ## Trees",
        content_hash="hash1234",
        tags=["dsa", "trees"],
    )

    vec_store.index_chunk(chunk)
    vec_store._save()

    assert Path(vec_file).exists()
    assert len(vec_store.vectors) == 1

    matches = vec_store.search("hierarchical binary trees", top_k=1)
    assert len(matches) == 1
    assert matches[0][0] == "chunk_01"
    assert matches[0][1] > 0.3


def test_incremental_vault_sync_and_purge(temp_vault_env):
    vault_dir, db_file, vec_file = temp_vault_env
    engine = KnowledgeEngine(vault_path=str(vault_dir), db_path=db_file, vector_index_path=vec_file)
    engine.init_vault()

    # 1. Add file
    dsa_file = vault_dir / "02_Learning/DSA.md"
    dsa_file.write_text("# Data Structures\n\n## Graph Algorithms\nBFS and DFS traversals.", encoding="utf-8")

    # Initial sync
    r1 = engine.sync()
    assert r1.files_indexed >= 1
    assert r1.total_chunks_created >= 1

    # 2. Second sync without edits -> all skipped
    r2 = engine.sync()
    assert r2.files_indexed == 0
    assert r2.files_skipped_unchanged >= 7

    # 3. Delete file -> purge detected
    dsa_file.unlink()
    r3 = engine.sync()
    assert r3.files_deleted_purged == 1


def test_hybrid_semantic_search_and_provenance(temp_vault_env):
    vault_dir, db_file, vec_file = temp_vault_env
    engine = KnowledgeEngine(vault_path=str(vault_dir), db_path=db_file, vector_index_path=vec_file)
    engine.init_vault()

    dbms_file = vault_dir / "04_References/DBMS_Deadlocks.md"
    dbms_file.write_text("""---
title: Database Deadlocks
tags: [dbms, os, concurrency]
---
# Database Management Systems

## Deadlock Prevention and Detection
A deadlock occurs when a set of processes are blocked because each process is holding a resource and waiting for another resource.
Techniques: Mutual exclusion avoidance, Hold and Wait prevention, Wait-Die scheme.
""", encoding="utf-8")

    engine.sync()

    # Perform hybrid search
    results = engine.search("how to prevent database deadlocks in concurrency", top_k=3)
    assert len(results) >= 1
    top_hit = results[0]
    assert "DBMS_Deadlocks.md" in top_hit.source_file
    assert top_hit.provenance_hash != ""
    assert top_hit.score > 0.2


def test_knowledge_security_boundaries(temp_vault_env):
    vault_dir, db_file, vec_file = temp_vault_env
    engine = KnowledgeEngine(vault_path=str(vault_dir), db_path=db_file, vector_index_path=vec_file)
    engine.init_vault()

    # 1. Sensitive Memory File
    mem_file = vault_dir / "05_Memory/private_thoughts.md"
    mem_file.write_text("# Personal Life Reflections\nConfidential life goals and private mental models.", encoding="utf-8")

    engine.sync()

    # 2. Unprivileged search (max_sensitivity = PUBLIC / INTERNAL) should NOT return sensitive memory
    unprivileged_hits = engine.search(
        query="confidential life goals",
        top_k=5,
        max_sensitivity=KnowledgeSensitivity.INTERNAL,
        actor_role="CodingAgent",
    )
    assert not any("private_thoughts.md" in h.source_file for h in unprivileged_hits)

    # 3. Privileged search by Alfred with SENSITIVE_MEMORY allowed
    privileged_hits = engine.retriever.search(
        query="confidential life goals",
        top_k=5,
        max_sensitivity=KnowledgeSensitivity.SENSITIVE_MEMORY,
        actor_role="AlfredMaster",
    )
    assert any("private_thoughts.md" in h.source_file for h in privileged_hits)


def test_alfred_context_composer(temp_vault_env):
    vault_dir, db_file, vec_file = temp_vault_env
    engine = KnowledgeEngine(vault_path=str(vault_dir), db_path=db_file, vector_index_path=vec_file)
    engine.init_vault()

    algo_file = vault_dir / "02_Learning/QuickSort.md"
    algo_file.write_text("# Algorithms\n\n## QuickSort\nDivide and conquer partition algorithm with O(N log N) expected time.", encoding="utf-8")
    engine.sync()

    context_str = engine.get_context_for_prompt("QuickSort algorithm expected time complexity", top_k=2)
    assert "RELEVANT KNOWLEDGE & OBSIDIAN VAULT CONTEXT" in context_str
    assert "Divide and conquer" in context_str
    assert "[Source:" in context_str
    assert "Hash:" in context_str
