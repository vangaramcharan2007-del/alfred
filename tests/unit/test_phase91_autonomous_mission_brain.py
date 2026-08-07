"""Unit Tests for Phase 91 Autonomous Mission Brain."""

import pytest
import shutil
from pathlib import Path
from jarvisx.agents.action_models import Capability, ActionProposal, RiskLevel, PolicyDecision
from jarvisx.agents.capability_registry import AutonomousCapabilityRegistry
from jarvisx.agents.mission_state import MissionStateMachine, State
from jarvisx.agents.policy_engine import PolicyEngine
from jarvisx.agents.goal_decomposer import GoalDecomposer
from jarvisx.agents.planner import StepPlanner
from jarvisx.agents.reflection_engine import ReflectionEngine
from jarvisx.agents.agent_executor import AutonomousAgentExecutor


def test_capability_registry_discovery():
    registry = AutonomousCapabilityRegistry()
    caps = registry.list_all()
    assert len(caps) >= 5

    # Semantic goal discovery
    matches = registry.discover_for_goal("synthesize exam revision notes")
    assert any(c.name == "document_generator" for c in matches)


def test_policy_engine_validation():
    policy = PolicyEngine(allow_high_risk=False)
    registry = AutonomousCapabilityRegistry()

    # Low risk allowed
    doc_cap = registry.get("document_generator")
    prop_low = ActionProposal("document_generator", {"output_dir": "var/test", "title": "T", "sections": {}}, "rationale", "outcome")
    res_low = policy.evaluate_proposal(prop_low, doc_cap)
    assert res_low["decision"] == PolicyDecision.ALLOW.value

    # High risk requires confirmation
    pkg_cap = registry.get("package_installer")
    prop_high = ActionProposal("package_installer", {"package_name": "pytest"}, "install", "installed")
    res_high = policy.evaluate_proposal(prop_high, pkg_cap)
    assert res_high["decision"] == PolicyDecision.ASK_USER.value

    # Forbidden path blocked
    prop_blocked = ActionProposal("document_generator", {"output_dir": r"c:\windows\system32", "title": "T", "sections": {}}, "rationale", "outcome")
    res_blocked = policy.evaluate_proposal(prop_blocked, doc_cap)
    assert res_blocked["decision"] == PolicyDecision.BLOCK.value


def test_mission_state_machine():
    sm = MissionStateMachine("test_01", "Test mission")
    assert sm.current_state == State.CREATED

    # Valid transitions
    sm.transition_to(State.PLANNING, "planning milestones")
    assert sm.current_state == State.PLANNING

    sm.transition_to(State.EXECUTING, "starting loop")
    assert sm.current_state == State.EXECUTING

    sm.transition_to(State.COMPLETED, "finished")
    assert sm.current_state == State.COMPLETED
    assert sm.is_finished() is True

    # Invalid transition raises error
    with pytest.raises(ValueError):
        sm.transition_to(State.PLANNING, "invalid")


def test_goal_decomposer_and_planner():
    decomposer = GoalDecomposer()
    decomp = decomposer.decompose("Create a Python calculator project")
    assert decomp["mission_name"] == "python_calculator"
    assert len(decomp["milestones"]) >= 3

    planner = StepPlanner()
    next_act = planner.get_next_action(decomp, completed_step_ids=[], mission_dir="var/test_calc")
    assert next_act is not None
    assert next_act.capability_name == "file_generator"


def test_agent_executor_react_loop():
    executor = AutonomousAgentExecutor()
    res = executor.execute_mission(
        goal="Create a Python calculator project",
        base_dir="var/test_missions"
    )

    test_dir = Path(res["mission_dir"])
    assert res["status"] == "SUCCESS"
    assert len(res["artifacts_created"]) >= 3
    assert (test_dir / "plan.json").exists()
    assert (test_dir / "execution_trace.json").exists()
    assert (test_dir / "src/calculator.py").exists()
    assert (test_dir / "tests/test_calculator.py").exists()
    assert (test_dir / "README.md").exists()
    assert (test_dir / "mission_report.md").exists()

    # Clean up test sandbox
    if test_dir.parent.exists():
        shutil.rmtree(test_dir.parent)
