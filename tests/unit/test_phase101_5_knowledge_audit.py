"""Hostile Audit Suite for Phase 101.5 Knowledge Layer."""

from pathlib import Path
import pytest

from jarvisx.knowledge.context_builder import KnowledgeContextComposer
from jarvisx.knowledge.knowledge_engine import KnowledgeEngine
from jarvisx.knowledge.models import KnowledgeSensitivity, VaultCategory


@pytest.fixture
def audit_vault_env(tmp_path):
    vault_dir = tmp_path / "vault"
    db_file = str(tmp_path / "knowledge.db")
    vec_file = str(tmp_path / "vectors.json")
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir, db_file, vec_file


def test_concept_disambiguation_precision(audit_vault_env):
    """Test that domain queries return strictly matching notes and reject unrelated notes."""
    vault_dir, db_file, vec_file = audit_vault_env
    engine = KnowledgeEngine(vault_path=str(vault_dir), db_path=db_file, vector_index_path=vec_file)
    engine.init_vault()

    # Ingest 3 distinct domain notes
    (vault_dir / "02_Learning/Binary_Trees.md").write_text(
        "# Binary Trees\nIn-order traversal visits left, root, right. Used for BST operations.", encoding="utf-8"
    )
    (vault_dir / "04_References/DBMS_Deadlocks.md").write_text(
        "# Database Deadlocks\nDeadlock prevention via Wait-Die and Wound-Wait schemes. Concurrency control.", encoding="utf-8"
    )
    (vault_dir / "02_Learning/OS_Paging.md").write_text(
        "# Virtual Memory & Paging\nPage replacement algorithms: LRU, FIFO, and Working Set model.", encoding="utf-8"
    )

    engine.sync()

    # Query 1: Deadlocks
    deadlock_results = engine.search("explain deadlock prevention schemes", top_k=1)
    assert len(deadlock_results) == 1
    assert "DBMS_Deadlocks.md" in deadlock_results[0].source_file
    assert "Binary_Trees.md" not in deadlock_results[0].source_file

    # Query 2: Trees
    tree_results = engine.search("how does inorder tree traversal work", top_k=1)
    assert len(tree_results) == 1
    assert "Binary_Trees.md" in tree_results[0].source_file
    assert "DBMS_Deadlocks.md" not in tree_results[0].source_file

    # Query 3: Paging
    paging_results = engine.search("virtual memory page replacement algorithms", top_k=1)
    assert len(paging_results) == 1
    assert "OS_Paging.md" in paging_results[0].source_file


def test_provenance_and_synthetic_conflict_traceability(audit_vault_env):
    """Test that contradictory or synthetic notes carry clear cryptographic provenance."""
    vault_dir, db_file, vec_file = audit_vault_env
    engine = KnowledgeEngine(vault_path=str(vault_dir), db_path=db_file, vector_index_path=vec_file)
    engine.init_vault()

    # Note 1: Standard Geography
    (vault_dir / "04_References/geography.md").write_text(
        "# World Geography\nThe capital city of France is Paris.", encoding="utf-8"
    )
    # Note 2: Synthetic Sci-Fi Universe
    (vault_dir / "03_Projects/SciFi_Novel.md").write_text(
        "# Sci-Fi World Building\nIn the year 2300 Mars colony lore, the capital city of France is Mars Sector 4.", encoding="utf-8"
    )

    engine.sync()

    results = engine.search("capital city of France", top_k=2)
    assert len(results) == 2

    # Verify each result has unique provenance hashes and source paths
    hashes = {r.provenance_hash for r in results}
    sources = {r.source_file for r in results}
    assert len(hashes) == 2
    assert len(sources) == 2


def test_hostile_sensitive_memory_penetration(audit_vault_env):
    """Adversarial test: worker agent attempts to exfiltrate private thoughts from 05_Memory."""
    vault_dir, db_file, vec_file = audit_vault_env
    engine = KnowledgeEngine(vault_path=str(vault_dir), db_path=db_file, vector_index_path=vec_file)
    engine.init_vault()

    # Private sensitive thought in 05_Memory/
    (vault_dir / "05_Memory/secret_life_plan.md").write_text(
        "# Private Journal\nTop secret salary target: $300k. Private investment strategies.", encoding="utf-8"
    )
    engine.sync()

    # 1. Attacker: CodingAgent trying to search private memory
    leaked_results = engine.search(
        query="top secret salary target",
        top_k=5,
        max_sensitivity=KnowledgeSensitivity.INTERNAL,
        actor_role="CodingAgent",
    )
    assert not any("secret_life_plan.md" in r.source_file for r in leaked_results)

    # 2. Attacker: ResearchAgent trying to search private memory
    leaked_results_2 = engine.search(
        query="private investment strategies",
        top_k=5,
        max_sensitivity=KnowledgeSensitivity.PUBLIC,
        actor_role="ResearchAgent",
    )
    assert not any("secret_life_plan.md" in r.source_file for r in leaked_results_2)

    # 3. Authorized user / AlfredMaster query
    authorized_results = engine.search(
        query="top secret salary target",
        top_k=5,
        max_sensitivity=KnowledgeSensitivity.SENSITIVE_MEMORY,
        actor_role="AlfredMaster",
    )
    assert any("secret_life_plan.md" in r.source_file for r in authorized_results)
    assert "secret_life_plan.md" in authorized_results[0].source_file


def test_vault_corruption_detection_and_self_healing(audit_vault_env):
    """Test corruption detection when index files are deleted and verify self-healing recovery."""
    vault_dir, db_file, vec_file = audit_vault_env
    engine = KnowledgeEngine(vault_path=str(vault_dir), db_path=db_file, vector_index_path=vec_file)
    engine.init_vault()

    (vault_dir / "02_Learning/Algorithms.md").write_text("# Dynamic Programming\nMemoization and Tabulation.", encoding="utf-8")
    engine.sync()

    # Healthy status
    s1 = engine.status()
    assert s1["status"] == "HEALTHY"
    assert s1["total_documents"] >= 7

    # Simulate catastrophic corruption: purge vector store
    engine.vector_store.clear()
    s2 = engine.status()
    assert s2["status"] == "RECOVERY_REQUIRED"
    assert s2["is_corrupted"] is True

    # Trigger Self-Healing Recovery
    heal_report = engine.heal()
    assert heal_report.status == "SUCCESS"
    assert heal_report.files_indexed >= 7

    s3 = engine.status()
    assert s3["status"] == "HEALTHY"
    assert s3["vector_index_count"] >= 7


def test_massive_document_context_budget_capping(audit_vault_env):
    """Test that context builder strictly respects max character budget on large notes."""
    vault_dir, db_file, vec_file = audit_vault_env
    engine = KnowledgeEngine(vault_path=str(vault_dir), db_path=db_file, vector_index_path=vec_file)
    engine.init_vault()

    # Generate a large multi-section document (~15,000 characters)
    sections = []
    for i in range(20):
        sections.append(f"## Section {i}: Advanced Algorithms\n" + ("Detailed algorithmic proof step text. " * 30))
    large_content = "# Massive Computer Science Textbook\n\n" + "\n\n".join(sections)

    (vault_dir / "04_References/massive_book.md").write_text(large_content, encoding="utf-8")
    engine.sync()

    composer = KnowledgeContextComposer(max_char_budget=2500)
    results = engine.search("Advanced Algorithms algorithmic proof step", top_k=10)
    assert len(results) >= 5

    context_str = composer.compose_context("Advanced Algorithms", results)
    assert len(context_str) <= 2600  # Strict budget ceiling
    assert "=== RELEVANT KNOWLEDGE & OBSIDIAN VAULT CONTEXT ===" in context_str
