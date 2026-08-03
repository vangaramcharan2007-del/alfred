from jarvisx.evolution.improvement_detector import ImprovementDetector

def test_improvement_detector():
    detector = ImprovementDetector()
    meta_report = {
        "improvement_plans": [
            {
                "title": "Upgrade Java debugger",
                "problem_statement": "Java debugging success rate 0.0%",
                "priority": 1,
                "action_items": ["Add Java AST parser", "Integrate Maven MCP"]
            }
        ]
    }
    proposals = detector.detect_proposals(meta_report)

    assert len(proposals) == 1
    assert proposals[0].priority == "HIGH"
    assert "Java AST parser" in proposals[0].proposed_solution
