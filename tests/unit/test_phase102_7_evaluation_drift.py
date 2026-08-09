"""Phase 102.7: Evaluation Drift Detection & Quality Degradation Test Suite."""

import pytest
from jarvisx.evaluation.drift_detector import DriftSeverity, EvaluationDriftDetector
from jarvisx.evaluation.evaluation_engine import EvaluationEngine
from jarvisx.evaluation.models import FailureCategory


@pytest.fixture
def drift_test_env(tmp_path):
    db_file = str(tmp_path / "evaluation.db")
    return db_file


def test_evaluation_drift_insufficient_data(drift_test_env):
    """Verify that insufficient evaluation history reports STABLE without false alarms."""
    engine = EvaluationEngine(db_path=drift_test_env)

    # Ingest only 3 evaluations
    for i in range(3):
        engine.evaluate_response(
            query=f"query {i}",
            answer=f"answer {i}",
            retrieved_chunks=[],
            response_id=f"r_{i}",
        )

    drift = engine.check_drift(min_evals=10)
    assert drift.is_drift_detected is False
    assert drift.severity == DriftSeverity.STABLE
    assert "Insufficient" in drift.diagnostics[0]


def test_evaluation_drift_stable_metrics(drift_test_env):
    """Verify that consistent high grounding and zero corrections produce STABLE status."""
    engine = EvaluationEngine(db_path=drift_test_env)

    # Ingest 15 high-quality accepted evaluations
    for i in range(15):
        eval_rec = engine.evaluate_response(
            query=f"Stable query {i}",
            answer=f"Accurate response with good grounding {i}",
            retrieved_chunks=[],
            response_id=f"r_stable_{i}",
        )
        # Explicitly accept all
        engine.record_user_acceptance(eval_rec.response_id)

    drift = engine.check_drift(min_evals=10)
    assert drift.is_drift_detected is False
    assert drift.severity == DriftSeverity.STABLE
    assert drift.grounding_drop_pct == 0.0


def test_evaluation_drift_warning_and_critical_degradation(drift_test_env):
    """Verify that substantial quality drops trigger WARNING and CRITICAL drift alerts."""
    engine = EvaluationEngine(db_path=drift_test_env)

    # 1. First ingest 10 baseline high-grounding accepted evaluations
    for i in range(10):
        e = engine.evaluate_response(
            query=f"Baseline query {i}",
            answer=f"High quality answer {i}",
            retrieved_chunks=[],
            response_id=f"r_base_{i}",
        )
        engine.record_user_acceptance(e.response_id)

    # 2. Ingest 10 heavily degraded and corrected responses
    for i in range(10):
        e = engine.evaluate_response(
            query=f"Degraded query {i}",
            answer=f"Poor answer {i}",
            retrieved_chunks=[],
            response_id=f"r_deg_{i}",
        )
        engine.record_user_correction(
            response_id=e.response_id,
            user_correction=f"Incorrect fact in answer {i}",
            category=FailureCategory.FACTUAL_ERROR,
            cause="Outdated note content",
        )

    drift = engine.check_drift(window_size=10, min_evals=10)
    assert drift.is_drift_detected is True
    assert drift.severity in (DriftSeverity.WARNING, DriftSeverity.CRITICAL)
    assert drift.current_correction_rate > drift.baseline_correction_rate
    assert len(drift.diagnostics) >= 1
    assert len(drift.recommended_actions) >= 1


def test_evaluation_drift_degraded_source_identification(drift_test_env):
    """Verify that specific degraded notes with repeated corrections are isolated."""
    engine = EvaluationEngine(db_path=drift_test_env)

    # Ingest 12 evaluations
    for i in range(12):
        engine.evaluate_response(
            query=f"Query {i}",
            answer=f"Answer {i}",
            retrieved_chunks=[],
            response_id=f"r_src_{i}",
        )

    bad_source = "04_References/outdated_api.md"

    # Repeatedly penalize the bad source
    for _ in range(5):
        engine.memory.update_source_utility(bad_source, retrieved=True, success=False, corrected=True)

    drift = engine.check_drift(min_evals=10)
    assert len(drift.degraded_sources) >= 1
    degraded_files = [d["source_file"] for d in drift.degraded_sources]
    assert bad_source in degraded_files
    assert any("outdated_api.md" in diag for diag in drift.diagnostics)
