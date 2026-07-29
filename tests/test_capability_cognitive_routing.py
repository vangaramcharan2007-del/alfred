from jarvisx.cognition.decision_engine import DecisionEngine

def test_capability_cognitive_routing():
    engine = DecisionEngine()
    
    # Context with capability reliability
    context = {
        "agent1": {
            "capability_match": 0.8,
            "capability_reliability": 0.9,
            "health_score": 1.0
        },
        "agent2": {
            "capability_match": 0.9,
            "capability_reliability": 0.3,
            "health_score": 0.5
        }
    }
    
    # Agent 1 should score higher due to better reliability and health, even though match is slightly lower
    ranked = engine.rank_agents(["agent1", "agent2"], context)
    assert ranked[0] == "agent1"
    assert ranked[1] == "agent2"
