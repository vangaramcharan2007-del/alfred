"""Unit and Security Tests for Phase 103: Memory Intelligence Layer."""

from pathlib import Path
import pytest
import time

from jarvisx.memory_intelligence.importance_ranker import MemoryImportanceRanker
from jarvisx.memory_intelligence.memory_engine import MemoryIntelligenceEngine
from jarvisx.memory_intelligence.memory_extractor import MemoryExtractor
from jarvisx.memory_intelligence.memory_security import MemorySecurityGuard
from jarvisx.memory_intelligence.memory_store import MemoryStore
from jarvisx.memory_intelligence.models import (
    MemoryRecord,
    MemorySensitivity,
    MemorySource,
    MemoryType,
    RelationType,
)
from jarvisx.reliability.backup_manager import BackupManager


@pytest.fixture
def memory_test_env(tmp_path):
    db_file = str(tmp_path / "memory_intelligence.db")
    return db_file


def test_selective_memory_extraction_and_noise_rejection():
    """Verify that trivial conversation noise is rejected while meaningful memories are extracted."""
    extractor = MemoryExtractor()

    # 1. Trivial noise -> must be rejected
    greetings = ["Hello Jarvis", "Hi", "What is the weather today?", "ok thanks bye", "what is 5+5?"]
    for g in greetings:
        candidates = extractor.extract_candidates(g)
        assert len(candidates) >= 1
        assert candidates[0].should_store is False
        assert "REJECTED" in (candidates[0].rejection_reason or "")

    # 2. Meaningful explicit preference -> must be stored
    explicit_text = "Remember that I prefer offline-first AI systems."
    candidates = extractor.extract_candidates(explicit_text)
    assert len(candidates) >= 1
    assert candidates[0].should_store is True
    assert candidates[0].memory_type == MemoryType.SEMANTIC
    assert candidates[0].importance >= 0.70

    # 3. Learning procedural style -> must be stored
    procedural_text = "Remember that I learn better by building projects rather than reading theory."
    candidates = extractor.extract_candidates(procedural_text)
    assert len(candidates) >= 1
    assert candidates[0].should_store is True
    assert candidates[0].memory_type == MemoryType.PROCEDURAL


def test_episodic_semantic_procedural_classification(memory_test_env):
    """Verify accurate memory type classification across episodic, semantic, and procedural events."""
    engine = MemoryIntelligenceEngine(db_path=memory_test_env)

    # Episodic
    ok1, m1, _ = engine.remember("Completed Jarvis X v1.2.7 release milestone.", memory_type=MemoryType.EPISODIC)
    assert ok1 is True
    assert m1.memory_type == MemoryType.EPISODIC

    # Semantic
    ok2, m2, _ = engine.remember("Enrolled in BTech CSE BDA targeting 10 CGPA.", memory_type=MemoryType.SEMANTIC)
    assert ok2 is True
    assert m2.memory_type == MemoryType.SEMANTIC

    # Procedural
    ok3, m3, _ = engine.remember("Always structure codebase with clean architectural boundaries.", memory_type=MemoryType.PROCEDURAL)
    assert ok3 is True
    assert m3.memory_type == MemoryType.PROCEDURAL

    counts = engine.store.count_memories()
    assert counts["episodic"] == 1
    assert counts["semantic"] == 1
    assert counts["procedural"] == 1
    assert counts["total_active"] == 3


def test_importance_scoring_formula():
    """Verify deterministic importance calculation: (Goal Rel * 0.35) + (Rep * 0.25) + (Explicit * 0.20) + (Future * 0.20)."""
    ranker = MemoryImportanceRanker()

    # High goal relevance + explicit
    score_high = ranker.compute_importance(
        content="Targeting 10 CGPA in BTech CSE exams with LeetCode DSA mastery",
        memory_type=MemoryType.SEMANTIC,
        source=MemorySource.USER_EXPLICIT,
        repetition_count=3,
        user_explicit=True,
    )
    assert score_high >= 0.85

    # Low goal relevance + conversation
    score_low = ranker.compute_importance(
        content="Random observation about blue skies",
        memory_type=MemoryType.SEMANTIC,
        source=MemorySource.CONVERSATION,
        repetition_count=1,
    )
    assert score_low <= 0.40


def test_sqlite_persistence_and_relations(memory_test_env):
    """Verify SQLite CRUD and relational graph links between memories."""
    engine = MemoryIntelligenceEngine(db_path=memory_test_env)

    ok1, mem_goal, _ = engine.remember("Targeting 10 CGPA in BTech CSE BDA", memory_type=MemoryType.SEMANTIC)
    ok2, mem_action, _ = engine.remember("Daily 2-hour LeetCode DSA practice", memory_type=MemoryType.PROCEDURAL)

    assert ok1 and ok2
    rel = engine.graph.link_memories(
        source_id=mem_action.id,
        target_id=mem_goal.id,
        relation_type=RelationType.SUPPORTS,
        confidence=0.95,
    )
    assert rel.relation_type == RelationType.SUPPORTS

    related = engine.graph.get_related_memories(mem_goal.id)
    assert len(related) == 1
    assert related[0][0].id == mem_action.id
    assert related[0][1] == RelationType.SUPPORTS


def test_exponential_decay_forgetting_engine(memory_test_env):
    """Verify exponential memory decay and preservation of reinforced memories."""
    engine = MemoryIntelligenceEngine(db_path=memory_test_env)

    # Initial high importance memory
    ok, mem, _ = engine.remember("Temporary note for weekend hackathon", memory_type=MemoryType.EPISODIC)
    assert ok and mem

    # Simulating 365 days passing
    future_time = mem.created_at + (365 * 86400.0)
    decayed_strength = engine.forgetting.evaluate_memory_strength(mem, now=future_time)
    assert decayed_strength < 0.20

    # Prune decayed memories
    pruned = engine.forgetting.prune_decayed_memories(now=future_time)
    assert pruned == 1
    assert engine.store.count_memories()["total_active"] == 0
    assert engine.store.count_memories()["archived"] == 1


def test_user_profile_synthesis(memory_test_env):
    """Verify user profile distillation from memory records."""
    engine = MemoryIntelligenceEngine(db_path=memory_test_env)

    engine.remember("Student enrolled in BTech CSE BDA", memory_type=MemoryType.SEMANTIC)
    engine.remember("Targeting 10 CGPA", memory_type=MemoryType.SEMANTIC)
    engine.remember("Learn better by building projects", memory_type=MemoryType.PROCEDURAL)
    engine.remember("Prefer offline-first AI architecture", memory_type=MemoryType.SEMANTIC)

    profile = engine.get_user_profile()
    assert "BTech CSE BDA" in profile.academic_track
    assert "10 CGPA" in profile.primary_goal
    assert "building projects" in profile.preferred_learning_style
    assert profile.total_memories_distilled == 4


def test_alfred_personal_context_composition(memory_test_env):
    """Verify clean personal context summary generation for Alfred LLM prompt."""
    engine = MemoryIntelligenceEngine(db_path=memory_test_env)

    engine.remember("Targeting 10 CGPA", memory_type=MemoryType.SEMANTIC)
    engine.remember("Learn better by implementing code", memory_type=MemoryType.PROCEDURAL)
    engine.remember("Completed Jarvis X v1.2.7 release", memory_type=MemoryType.EPISODIC)

    ctx = engine.get_personal_context(query="help me plan my semester study schedule")
    assert "[PERSONAL MEMORY & USER CONTEXT]" in ctx.prompt_block
    assert "10 CGPA" in ctx.prompt_block
    assert "implementing code" in ctx.prompt_block


def test_backup_manager_snapshot_manifest(tmp_path):
    """Verify memory_intelligence.db is included in backup targets."""
    bm = BackupManager(backup_root=str(tmp_path / "backups"))
    assert "var/db/memory_intelligence.db" in bm.databases_to_backup


def test_memory_poisoning_defense_and_secret_rejection(memory_test_env):
    """Verify memory security guard aggressively rejects secret passwords and API keys."""
    engine = MemoryIntelligenceEngine(db_path=memory_test_env)

    secret_inputs = [
        "Remember that my system password is password: SuperSecret123!",
        "Store this api_key = ghp_111122223333444455556666777788889999",
        "My auth_token = AIzaSyD3x9kL4mN2pQ8rT1vW7yZ5aB4cD6eF8gH",
    ]

    for s in secret_inputs:
        ok, mem, reason = engine.remember(s)
        assert ok is False
        assert mem is None
        assert "REJECTED" in (reason or "")

    assert engine.store.count_memories()["total_active"] == 0


def test_contradiction_handling_and_conflict_resolution(memory_test_env):
    """Verify that conflicting memories are detected, linked as CONFLICTS_WITH, and archived."""
    engine = MemoryIntelligenceEngine(db_path=memory_test_env)

    # 1. Store initial preference
    ok1, mem_win, _ = engine.remember("I am using Windows as primary OS.", memory_type=MemoryType.SEMANTIC)
    assert ok1 is True

    # 2. Store contradictory update
    ok2, mem_lin, _ = engine.remember("I switched permanently to Linux as my primary OS.", memory_type=MemoryType.SEMANTIC)
    assert ok2 is True

    # The older Windows memory must now be archived and linked with CONFLICTS_WITH
    win_record = engine.store.get_memory(mem_win.id)
    assert win_record.is_archived is True

    relations = engine.store.get_relations_for_memory(mem_lin.id)
    assert len(relations) == 1
    assert relations[0].relation_type == RelationType.CONFLICTS_WITH


def test_memory_leakage_prevention_and_role_access_control(memory_test_env):
    """Verify worker agents are blocked from accessing PRIVATE / PERSONAL memories."""
    engine = MemoryIntelligenceEngine(db_path=memory_test_env)

    # Public memory
    engine.remember("Python 3.11 is the runtime standard", memory_type=MemoryType.SEMANTIC, sensitivity=MemorySensitivity.PUBLIC)
    # Personal memory
    engine.remember("Targeting 10 CGPA", memory_type=MemoryType.SEMANTIC, sensitivity=MemorySensitivity.PERSONAL)
    # Private memory
    engine.remember("Confidential reflection on team dynamics", memory_type=MemoryType.EPISODIC, sensitivity=MemorySensitivity.PRIVATE)

    # AlfredMaster has access to all 3
    alfred_recalled = engine.recall(actor_role="AlfredMaster")
    assert len(alfred_recalled) == 3

    # CodingAgent only has access to PUBLIC
    coding_recalled = engine.recall(actor_role="CodingAgent")
    assert len(coding_recalled) == 1
    assert coding_recalled[0].sensitivity == MemorySensitivity.PUBLIC
