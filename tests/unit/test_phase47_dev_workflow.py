"""Unit and verification tests for Phase 47: Development Workflow Automation.

Verifies end-to-end closed loop execution (Planning -> Coding -> AST checking ->
Testing -> Git Diff -> Human Approval), syntax error abortion, and empirical HSPW tracking.
"""

import pytest
from jarvisx.agents import CodingAgent
from jarvisx.automation import DevelopmentWorkflow, WorkflowStage


def test_coding_agent_syntax_validation_and_diff():
    """Verify CodingAgent performs static AST validation and formats unified git diffs."""
    coder = CodingAgent()

    # Valid syntax check
    res_valid = coder.validate_syntax("def test_fn():\n    return 42\n", "src/valid.py")
    assert res_valid["valid"] is True

    # Invalid syntax check
    res_invalid = coder.validate_syntax("def broken(: return", "src/invalid.py")
    assert res_invalid["valid"] is False
    assert "SyntaxError" in res_invalid["error"]

    # Diff generation
    diff_res = coder.generate_diff("src/test.py", "old_line\n", "new_line\n")
    assert "--- a/src/test.py" in diff_res["diff"]
    assert "+++ b/src/test.py" in diff_res["diff"]


def test_development_workflow_loop_to_review_stage():
    """Verify DevelopmentWorkflow progresses through planning, coding, tests, and stages for review."""
    workflow = DevelopmentWorkflow()

    summary = workflow.run_loop(
        objective="Implement JWT Auth Handler",
        target_file="src/auth_handler.py",
        sample_code="def verify_token(tok: str) -> bool:\n    return bool(tok)\n",
    )

    assert workflow.current_stage == WorkflowStage.STAGED_FOR_REVIEW
    assert summary["ast_verified"] is True
    assert summary["test_verified"] is True
    assert "ALFRED DEVELOPMENT WORKFLOW STAGING" in summary["output"]
    assert "Action Required: Awaiting supervisor call to approve_and_merge()" in summary["output"]

    # Supervisor approves and merges
    approval = workflow.approve_and_merge()
    assert approval["status"] == "success"
    assert workflow.current_stage == WorkflowStage.APPROVED
    # Workforce HSPW: researcher (0.4) + coder (1.2) + tester (0.3) + coder AST check (1.2) = ~3.1 hrs per run
    assert approval["workforce_hspw"] > 0.0


def test_development_workflow_rejection():
    """Verify supervisor rejection terminates workflow at REJECTED stage."""
    workflow = DevelopmentWorkflow()
    workflow.run_loop("Simple Refactor", sample_code="x = 100\n")
    rej = workflow.reject("Requires stricter type annotations")
    assert rej["status"] == "rejected"
    assert workflow.current_stage == WorkflowStage.REJECTED


def test_development_workflow_ast_failure_aborts_loop():
    """Verify invalid Python code synthesis immediately fails at STATIC_ANALYSIS without staging."""
    workflow = DevelopmentWorkflow()
    outcome = workflow.run_loop("Broken Scoped Feature", sample_code="def bad_syntax(: return")
    assert outcome["status"] == "failed"
    assert workflow.current_stage == WorkflowStage.FAILED
    assert "SyntaxError" in outcome["error"]
    assert workflow.ast_verified is False
