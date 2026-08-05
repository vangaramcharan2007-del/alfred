"""Unit and verification tests for Phase 52: External VCS & CI/CD Automation.

Verifies automated Pull Request packaging, bug issue triaging, release bundling,
quantified HSPW savings (> +6.0 HSPW across standard batch runs), and Layer 3 compliance.
"""

import pytest
from jarvisx.automation.vcs_ci import VCSEngine
from jarvisx.agents.devops import DevOpsAgent
from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.architecture import get_layer_for_module


def test_vcs_engine_pr_triage_release():
    """Verify zero-fluff VCSEngine executes PR creation, issue diagnosis, and release tagging."""
    engine = VCSEngine()

    # 1. Package Pull Request
    pr_res = engine.create_pull_request(title="Add Token Auth", description="Implements JWT handler", source_branch="feat-auth")
    assert pr_res["status"] == "success"
    assert pr_res["pull_request"]["mergeable_status"] == "MERGEABLE_GREEN"

    # 2. Triage Incoming Bug Issue
    issue_res = engine.triage_issue(title="Pytest failure on socket timeout", body="Crash occurs when asserting mock port in unit suite")
    assert issue_res["status"] == "triaged"
    assert issue_res["issue"]["priority"] == "P1_CRITICAL"
    assert issue_res["issue"]["assigned_agent"] == "testing_agent"

    # 3. Bundle Semantic Release
    rel_res = engine.package_release(version_tag="v2.0.0", release_notes="Sovereign Epoch release.")
    assert rel_res["status"] == "ready"
    assert rel_res["release"]["verified_tests_count"] == 74


def test_devops_agent_and_personal_os_routing(monkeypatch):
    """Verify DevOpsAgent executes workflows and accumulates +6.0+ HSPW when integrated into Alfred Personal OS."""
    os_kernel = PersonalOSKernel()
    monkeypatch.setattr(os_kernel.guardian_agent.guardian.git_watcher, "check_git_status", lambda cwd: {"status": "CLEAN", "uncommitted_count": 0})

    # Execute 4 automated DevOps objectives via Personal OS command interface
    os_kernel.execute_objective("Create pull request for auth enhancement", title="Feat Auth PR", branch="feat-auth")
    os_kernel.execute_objective("Triage issue regarding database latency exception", title="DB Timeout Exception", body="Crash on slow query")
    os_kernel.execute_objective("Triage issue regarding documentation updates", title="Update Readme", body="Study notes for API docs")
    os_kernel.execute_objective("Package release for v2.0.0", version="v2.0.0", notes="Full autonomous stack")

    # Verify agent accumulated HSPW time savings (4 * 1.5 HSPW = 6.0 HSPW!)
    devops_worker = os_kernel.devops_agent
    assert devops_worker.metrics()["hours_saved"] >= 6.0

    # Verify Master Dashboard reports DevOps status cleanly
    dashboard = os_kernel.get_master_dashboard()
    assert "[DEVOPS & RELEASE ENGINEERING]" in dashboard["output"]
    assert "Active Pull Requests: 1" in dashboard["output"]
    assert "Triaged Issues: 2" in dashboard["output"]
    assert "Staged Releases: 1" in dashboard["output"]


def test_architecture_layer_compliance_for_vcs_devops():
    """Verify VCSEngine and DevOpsAgent align to established architectural layer boundaries."""
    assert get_layer_for_module("jarvisx.automation.vcs_ci") == "agents"
    assert get_layer_for_module("jarvisx.agents.devops") == "agents"
