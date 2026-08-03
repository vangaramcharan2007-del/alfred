import pytest
from jarvisx.capabilities.coding.pipeline.repository_analyzer import RepositoryContext
from jarvisx.capabilities.coding.pipeline.task_planner import TaskPlanner

def test_task_planner_calculator():
    ctx = RepositoryContext(
        root_path="/tmp/fake",
        primary_language="python",
        framework="FastAPI",
        files_count=5,
        key_files=["main.py"],
        has_tests=True
    )
    planner = TaskPlanner()
    plan = planner.plan_task("Add a calculator API endpoint to this FastAPI project", ctx)

    assert len(plan.steps) >= 3
    assert any(step.action_type == "test" for step in plan.steps)
    assert any(step.action_type == "review" for step in plan.steps)
    plan_dict = plan.to_dict()
    assert "steps" in plan_dict
