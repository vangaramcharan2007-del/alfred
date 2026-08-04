import pytest
from jarvisx.brain.dynamic_planner import DynamicTaskPlanner, RiskLevel

def test_unknown_goal_planning():
    planner = DynamicTaskPlanner()
    plan = planner.generate_plan("Build a simple expense tracker")
    
    assert plan.objective == "Build a simple expense tracker"
    assert len(plan.tasks) >= 3
    assert plan.tasks[0].task_id == "T01"
    assert plan.tasks[1].dependencies == ["T01"]
    assert plan.estimated_risk in (RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH)
