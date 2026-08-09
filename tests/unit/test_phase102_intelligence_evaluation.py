"""Unit Tests for Phase 102 Evidence-Based Intelligence Evaluation Layer."""

from pathlib import Path
import pytest

from jarvisx.evaluation.evidence.evidence_tracker import EvidenceTracker
from jarvisx.evaluation.models import (
    EvidenceSupportState,
    FailureCategory,
    ResponseEvaluation,
)
from jarvisx.evaluation.scoring.quality_metrics import QualityMetricsAggregator
from jarvisx.evaluation.scoring.response_scorer import ResponseScorer
from jarvisx.evaluation.scoring.retrieval_evaluator import RetrievalEvaluator
from jarvisx.evaluation.storage.feedback_memory import FeedbackMemory
from jarvisx.evaluation.evaluation_engine import EvaluationEngine
from jarvisx.knowledge.models import KnowledgeSensitivity, SearchResult


@pytest.fixture
def eval_temp_env(tmp_path):
    db_file = str(tmp_path / "evaluation.db")
    return db_file


def test_evidence_tracker_claim_extraction_and_support_states():
    """Test claim extraction and classification into SUPPORTED, PARTIALLY_SUPPORTED, and UNKNOWN_FROM_VAULT."""
    tracker = EvidenceTracker()

    sample_chunks = [
        SearchResult(
            chunk_id="chunk_bst_1",
            source_file="02_Learning/Binary_Trees.md",
            content="A Binary Search Tree maintains invariant left < root < right. Search is O(log N) on average.",
            heading_path="# Binary Trees > ## Invariant",
            score=0.88,
            relevance_reason="semantic_similarity",
            sensitivity=KnowledgeSensitivity.INTERNAL,
            tags=["dsa", "trees"],
            provenance_hash="hash_bst_01",
        )
    ]

    response_text = """
    A Binary Search Tree maintains the invariant that the left child is less than root.
    Search operations run in O(log N) average time.
    Python was created by Guido van Rossum in 1989.
    """

    trace = tracker.build_trace(
        response_id="resp_001",
        query="explain binary search tree invariant and complexity",
        response_text=response_text,
        retrieved_chunks=sample_chunks,
    )

    assert trace.response_id == "resp_001"
    assert len(trace.claims) >= 3

    # BST claims should be SUPPORTED
    bst_claims = [c for c in trace.claims if "binary search tree" in c.claim_text.lower() or "o(log n)" in c.claim_text.lower()]
    assert any(c.support_state == EvidenceSupportState.SUPPORTED for c in bst_claims)

    # Python claim not in note should be UNKNOWN_FROM_VAULT
    python_claim = [c for c in trace.claims if "python" in c.claim_text.lower()][0]
    assert python_claim.support_state in (EvidenceSupportState.UNKNOWN_FROM_VAULT, EvidenceSupportState.UNSUPPORTED)

    assert trace.grounding_ratio > 0.4
    assert len(trace.sources) >= 1
    assert trace.sources[0].source_file == "02_Learning/Binary_Trees.md"


def test_retrieval_evaluator_metrics_and_depth():
    """Test pre-generation retrieval quality evaluation."""
    evaluator = RetrievalEvaluator()

    chunks = [
        SearchResult(
            chunk_id="c1",
            source_file="04_References/Deadlocks.md",
            content="Deadlock prevention via Wait-Die and Wound-Wait schemes.",
            heading_path="# Deadlocks",
            score=0.75,
            relevance_reason="semantic_similarity (0.75) + matched_keywords [deadlock]",
            sensitivity=KnowledgeSensitivity.PUBLIC,
            tags=["dbms", "os"],
            provenance_hash="hash_dl_01",
        ),
        SearchResult(
            chunk_id="c2",
            source_file="02_Learning/OS.md",
            content="Operating system resource allocation graphs.",
            heading_path="# OS",
            score=0.45,
            relevance_reason="semantic_similarity (0.45)",
            sensitivity=KnowledgeSensitivity.INTERNAL,
            tags=["os"],
            provenance_hash="hash_os_01",
        ),
    ]

    res = evaluator.evaluate_retrieval("deadlock prevention schemes", chunks)
    assert res.total_retrieved == 2
    assert res.top_score == 0.75
    assert res.has_strong_grounding is True
    assert res.retrieval_relevance_score > 0.6
    assert "04_References/Deadlocks.md" in res.top_sources


def test_response_scorer_deterministic_formula_and_penalties():
    """Test response quality score calculation and correction penalty deductions."""
    scorer = ResponseScorer()
    evaluator = RetrievalEvaluator()
    tracker = EvidenceTracker()

    chunks = [
        SearchResult(
            chunk_id="c1",
            source_file="02_Learning/QuickSort.md",
            content="QuickSort is a divide and conquer sorting algorithm with O(N log N) average complexity.",
            heading_path="# QuickSort",
            score=0.85,
            relevance_reason="semantic_similarity",
            sensitivity=KnowledgeSensitivity.INTERNAL,
            tags=["dsa"],
            provenance_hash="hash_qs_01",
        )
    ]

    query = "explain quicksort algorithm"
    answer = "QuickSort is a divide and conquer sorting algorithm with expected time complexity of O(N log N)."

    ret_eval = evaluator.evaluate_retrieval(query, chunks)
    trace = tracker.build_trace("resp_qs", query, answer, chunks)

    # 1. Base evaluation without penalties
    eval_record = scorer.score_response(
        response_id="resp_qs",
        query=query,
        response_text=answer,
        retrieval_eval=ret_eval,
        evidence_trace=trace,
    )
    assert eval_record.grounding_score >= 0.8
    assert eval_record.final_quality_score >= 0.75
    assert eval_record.user_correction_penalty == 0.0

    # 2. Evaluation with user correction penalty (-0.20)
    penalized_eval = scorer.score_response(
        response_id="resp_qs",
        query=query,
        response_text=answer,
        retrieval_eval=ret_eval,
        evidence_trace=trace,
        user_correction_penalty=0.20,
    )
    assert penalized_eval.user_correction_penalty == 0.20
    assert penalized_eval.final_quality_score == round(eval_record.final_quality_score - 0.20, 4)


def test_feedback_memory_sqlite_persistence(eval_temp_env):
    """Test SQLite storage for evaluations, failures, and source utility."""
    memory = FeedbackMemory(db_path=eval_temp_env)

    eval_rec = ResponseEvaluation(
        response_id="resp_test_01",
        query="What is a binary tree?",
        answer_snippet="A tree where each node has at most two children.",
        grounding_score=0.95,
        completeness_score=0.85,
        clarity_score=0.90,
        retrieval_confidence=0.88,
        user_correction_penalty=0.0,
        final_quality_score=0.91,
        actor_role="AlfredMaster",
    )

    memory.save_evaluation(eval_rec)

    fetched = memory.get_evaluation("resp_test_01")
    assert fetched is not None
    assert fetched.response_id == "resp_test_01"
    assert fetched.grounding_score == 0.95
    assert fetched.final_quality_score == 0.91

    last = memory.get_last_evaluation()
    assert last is not None
    assert last.response_id == "resp_test_01"


def test_user_correction_sanitization_and_failure_logging(eval_temp_env):
    """Test user correction logging, input sanitization, and penalty deduction."""
    memory = FeedbackMemory(db_path=eval_temp_env)

    eval_rec = ResponseEvaluation(
        response_id="resp_err_01",
        query="Are Python tuples mutable?",
        answer_snippet="Python tuples are mutable objects.",
        grounding_score=0.40,
        completeness_score=0.70,
        clarity_score=0.80,
        retrieval_confidence=0.50,
        user_correction_penalty=0.0,
        final_quality_score=0.57,
        actor_role="AlfredMaster",
    )
    memory.save_evaluation(eval_rec)

    # Simulate hostile correction with HTML/script injection
    engine = EvaluationEngine(db_path=eval_temp_env)
    updated = engine.record_user_correction(
        response_id="resp_err_01",
        user_correction="<script>alert('pwn')</script>Tuples are immutable in Python.",
        category=FailureCategory.FACTUAL_ERROR,
        cause="Incorrect memory assertion.",
    )

    assert updated is not None
    assert updated.user_correction_penalty == 0.20
    assert updated.final_quality_score < 0.40
    assert "<script>" not in (updated.user_feedback or "")
    assert "&lt;script&gt;" in (updated.user_feedback or "")

    failures = memory.list_failures()
    assert len(failures) == 1
    assert failures[0].response_id == "resp_err_01"
    assert failures[0].category == FailureCategory.FACTUAL_ERROR


def test_source_utility_tracking_and_learning(eval_temp_env):
    """Test historical source utility score updates."""
    memory = FeedbackMemory(db_path=eval_temp_env)

    source = "02_Learning/DSA_Master.md"

    # 1. First 3 successful retrievals
    memory.update_source_utility(source, retrieved=True, success=True, corrected=False)
    memory.update_source_utility(source, retrieved=True, success=True, corrected=False)
    u3 = memory.update_source_utility(source, retrieved=True, success=True, corrected=False)
    assert u3.times_retrieved == 3
    assert u3.times_successful == 3
    assert u3.utility_score == 1.0

    # 2. User corrected response that used this source
    u4 = memory.update_source_utility(source, retrieved=False, success=False, corrected=True)
    assert u4.times_corrected == 1
    assert u4.utility_score < 1.0


def test_intelligence_scorecard_aggregation(eval_temp_env):
    """Test QualityMetricsAggregator computing scorecards across multiple evaluations."""
    engine = EvaluationEngine(db_path=eval_temp_env)

    # Evaluate 3 sample responses
    engine.evaluate_response(
        query="Query 1",
        answer="Answer 1 with high quality structured text.\n- Point 1\n- Point 2",
        retrieved_chunks=[],
    )
    e2 = engine.evaluate_response(
        query="Query 2",
        answer="Answer 2",
        retrieved_chunks=[],
    )
    engine.record_user_acceptance(e2.response_id, "Looks great.")

    scorecard = engine.get_scorecard()
    assert scorecard.total_evaluations == 2
    assert scorecard.average_quality_score > 0.0
    assert scorecard.user_satisfaction_rate == 1.0


def test_evaluation_engine_end_to_end_flow(eval_temp_env):
    """Full end-to-end integration test of evaluation, feedback, and history."""
    engine = EvaluationEngine(db_path=eval_temp_env)

    chunk = SearchResult(
        chunk_id="c_graph",
        source_file="02_Learning/Graphs.md",
        content="Breadth First Search (BFS) uses a Queue and explores level-by-level.",
        heading_path="# Graphs > ## BFS",
        score=0.92,
        relevance_reason="semantic_similarity",
        sensitivity=KnowledgeSensitivity.INTERNAL,
        tags=["dsa", "graphs"],
        provenance_hash="hash_graph_01",
    )

    query = "explain breadth first search"
    answer = "Breadth First Search explores graph vertices level-by-level using a Queue FIFO structure."

    eval_record = engine.evaluate_response(
        query=query,
        answer=answer,
        retrieved_chunks=[chunk],
        actor_role="AlfredMaster",
    )

    assert eval_record.grounding_score >= 0.5
    assert eval_record.final_quality_score >= 0.65

    # Check history
    history = engine.list_history()
    assert len(history) == 1
    assert history[0].response_id == eval_record.response_id
