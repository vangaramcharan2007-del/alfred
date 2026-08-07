"""Unit Tests for Phase 92.5 Capability Intelligence Layer."""

import pytest
import time
from pathlib import Path
from jarvisx.skills.models import SkillMetadata, SkillStatus
from jarvisx.skills.skill_metrics import SkillMetricsTracker
from jarvisx.skills.skill_graph import SkillDependencyGraph
from jarvisx.skills.skill_evaluator import SkillEvaluator
from jarvisx.skills.skill_registry import PersistentSkillRegistry


def test_skill_metrics_tracking():
    metrics_file = "var/test_skills/test_metrics.json"
    if Path(metrics_file).exists():
        Path(metrics_file).unlink()

    tracker = SkillMetricsTracker(metrics_file)
    rec1 = tracker.record_usage("test_skill", success=True, duration_sec=1.5)
    assert rec1["times_used"] == 1
    assert rec1["success_rate"] == 1.0

    rec2 = tracker.record_usage("test_skill", success=False, duration_sec=2.5)
    assert rec2["times_used"] == 2
    assert rec2["success_rate"] == 0.5
    assert rec2["average_runtime_sec"] == 2.0


def test_skill_dependency_graph():
    graph_file = "var/test_skills/test_deps.json"
    if Path(graph_file).exists():
        Path(graph_file).unlink()

    graph = SkillDependencyGraph(graph_file)
    graph.register_dependency("flashcard_skill", ["ocr_skill", "document_generator"])

    deps = graph.get_dependencies("flashcard_skill")
    assert "ocr_skill" in deps

    affected = graph.get_affected_dependents("ocr_skill")
    assert "flashcard_skill" in affected


def test_skill_evaluator_ranking_and_retirement():
    metrics_file = "var/test_skills/test_eval_metrics.json"
    catalog_file = "var/test_skills/test_eval_catalog.json"
    if Path(metrics_file).exists():
        Path(metrics_file).unlink()
    if Path(catalog_file).exists():
        Path(catalog_file).unlink()

    tracker = SkillMetricsTracker(metrics_file)
    registry = PersistentSkillRegistry(catalog_file)

    meta_bad = SkillMetadata(name="bad_skill", status=SkillStatus.INSTALLED)
    registry.register_installed_skill(meta_bad)

    # Simulate 5 failures
    for _ in range(5):
        tracker.record_usage("bad_skill", success=False, duration_sec=3.0)

    evaluator = SkillEvaluator(tracker, registry)
    retired = evaluator.evaluate_and_retire_underperforming_skills(failure_threshold=0.35)
    assert "bad_skill" in retired

    updated_meta = registry.get_skill_metadata("bad_skill")
    assert updated_meta.status == SkillStatus.DISABLED
