"""Unit and Integration Tests for Phase 75: Personal Memory & Proactive Intelligence Engine.

Tests MemoryClassifier, ImportanceEngine, ContextRetriever, GoalTracker,
ProactiveIntelligenceEngine, ProactiveMissionBridge, and ProactiveSafetyGuard.
"""

import os
import sys
import time
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.memory.intelligence import MemoryClassifier, ImportanceEngine, ContextRetriever
from jarvisx.goals import GoalTracker
from jarvisx.intelligence import ProactiveIntelligenceEngine, ProactiveMissionBridge, ProactiveSafetyGuard


def test_memory_classifier():
    """Verify MemoryClassifier categorizes text into preference, task, goal, deadline, habit, knowledge."""
    classifier = MemoryClassifier()

    assert classifier.classify_text("Calculus exam due by Friday") == "deadline"
    assert classifier.classify_text("Always use VS Code for coding") == "preference"
    assert classifier.classify_text("Long-term goal: learn machine learning") == "goal"
    assert classifier.classify_text("I usually study algorithms at 8 PM daily") == "habit"
    assert classifier.classify_text("Todo task: finish assignment") == "task"
    assert classifier.classify_text("Definition of linear algebra formula") == "knowledge"
    assert classifier.classify_text("Hello random statement") == "temporary context"


def test_importance_engine_formula():
    """Verify ImportanceEngine computes importance = frequency + recency + future_usefulness."""
    engine = ImportanceEngine(half_life_seconds=86400.0)
    now = time.time()

    res = engine.compute_importance(frequency=5, created_at=now, category="goal", now=now)
    assert res["importance"] > 0.0
    assert "frequency_score" in res
    assert "recency_score" in res
    assert "future_usefulness_score" in res
    # Goal category should have high future usefulness score (5.0)
    assert res["future_usefulness_score"] == 5.0


def test_context_retriever():
    """Verify ContextRetriever retrieves objective-matched memories."""
    retriever = ContextRetriever()
    memories = retriever.retrieve_relevant_context(current_objective="organize downloads", top_k=3)
    assert isinstance(memories, list)


def test_goal_tracker_lifecycle():
    """Verify GoalTracker supports long-term goals, short-term objectives, deadlines, and SQLite persistence."""
    tracker = GoalTracker()

    g1 = tracker.add_goal("Learn Machine Learning", goal_type="LONG_TERM", next_action="Read chapter 1")
    assert g1["goal"] == "Learn Machine Learning"
    assert g1["type"] == "LONG_TERM"
    assert g1["status"] == "IN_PROGRESS"

    g2 = tracker.add_goal("Complete Calculus Assignment", goal_type="DEADLINE", deadline="Tomorrow 5 PM")
    assert g2["type"] == "DEADLINE"

    active = tracker.get_active_goals()
    assert len(active) >= 2

    # Test updating goal progress
    updated = tracker.update_goal_progress(g1["goal_id"], progress=1.0)
    assert updated["status"] == "COMPLETED"


def test_proactive_intelligence_engine_and_mission_bridge():
    """Verify ProactiveIntelligenceEngine generates evidence-backed suggestions and converts them into Missions."""
    kernel = PersonalOSKernel()
    kernel.execute_objective("add goal", goal="Master Quantum Computing", type="LONG_TERM", next_action="Read paper")

    proactive = kernel.proactive_engine
    suggestions = proactive.generate_proactive_suggestions(os_kernel=kernel)
    assert len(suggestions) >= 1

    sug = suggestions[0]
    assert "title" in sug
    assert "reason" in sug
    assert "evidence" in sug

    # Convert suggestion to Mission
    bridge = kernel.proactive_bridge
    mission = bridge.convert_suggestion_to_mission(sug)
    assert mission.title == sug["title"]
    assert mission.status == "PENDING"
    assert mission.context["reason"] == sug["reason"]


def test_proactive_safety_guard():
    """Verify ProactiveSafetyGuard enforces confidence thresholds and requires confirmation for impactful actions."""
    kernel = PersonalOSKernel()
    guard = kernel.proactive_safety

    # Safe low-impact suggestion with high confidence
    s1 = {"title": "Start Study Session", "suggestion": "Study algorithms", "confidence": 0.85}
    e1 = guard.evaluate_proactive_safety(s1, user_confirmed=False)
    assert e1["permitted"] is True

    # Low confidence suggestion
    s2 = {"title": "Random Guess", "suggestion": "Do something", "confidence": 0.50}
    e2 = guard.evaluate_proactive_safety(s2, user_confirmed=False)
    assert e2["permitted"] is False
    assert e2["status"] == "BLOCKED_LOW_CONFIDENCE"

    # Impactful action (e.g. delete file / format disk) without user confirmation
    s3 = {"title": "Delete File Staging", "suggestion": "delete file from downloads", "confidence": 0.95}
    e3 = guard.evaluate_proactive_safety(s3, user_confirmed=False)
    assert e3["permitted"] is False
    assert e3["status"] == "REQUIRES_USER_CONFIRMATION"

    # Impactful action WITH user confirmation
    e3_conf = guard.evaluate_proactive_safety(s3, user_confirmed=True)
    assert e3_conf["permitted"] is True
