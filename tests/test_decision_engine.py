import pytest
from jarvisx.cognition.decision_engine import DecisionEngine

def test_decision_engine_evaluation():
    engine = DecisionEngine()
    context = {
        "capability_match": 1.0,
        "historical_success": 0.8,
        "preference_match": 0.5,
        "task_similarity": 0.2,
        "confidence_score": 0.9
    }
    score = engine.evaluate("test_agent", context)
    assert score > 0

def test_decision_engine_ranking():
    engine = DecisionEngine()
    context = {
        "agent1": {"capability_match": 1.0},
        "agent2": {"capability_match": 0.5}
    }
    ranked = engine.rank_agents(["agent1", "agent2"], context)
    assert ranked[0] == "agent1"
