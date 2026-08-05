"""Unit and verification tests for Phase 50: Personal OS & Full Lifecycle Integration.

Verifies intelligent intent routing across academic study schedules, engineering code builds,
and background system hygiene, while validating total cumulative HSPW metrics and Layer 2 compliance.
"""

import pytest
from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.architecture import get_layer_for_module


def test_personal_os_kernel_boot_and_workforce():
    """Verify PersonalOSKernel boots in Layer 2 and initializes all operational workers."""
    os_kernel = PersonalOSKernel()
    health = os_kernel.registry.health()
    assert health["total_workers"] == 5  # Research, Testing, Coding, Productivity, Guardian
    assert os_kernel.dev_workflow.current_stage.value == "INITIATED"


def test_personal_os_objective_routing_and_dashboard(monkeypatch):
    """Verify intelligent objective routing across study, engineering, and monitoring capabilities."""
    os_kernel = PersonalOSKernel()

    # Isolate guardian git check for stable verification
    monkeypatch.setattr(os_kernel.guardian_agent.guardian.git_watcher, "check_git_status", lambda cwd: {"status": "CLEAN", "uncommitted_count": 0})

    # 1. Route study objective
    res_study = os_kernel.execute_objective("Schedule revision for Distributed Systems exam", course="Distributed Systems", topics="RAFT, Paxos, Vector Clocks".split(", "), days_until_exam=4)
    assert res_study["status"] == "completed"

    # 2. Route engineering development objective
    res_dev = os_kernel.execute_objective("Develop JWT Token Refresher", target_file="src/auth.py", sample_code="def refresh():\n    return 'jwt'\n")
    assert res_dev["status"] == "staged"

    # 3. Route health audit objective
    res_health = os_kernel.execute_objective("Run project health audit sweep")
    assert res_health["status"] == "completed"

    # 4. Generate master command dashboard
    dashboard = os_kernel.get_master_dashboard()
    assert dashboard["status"] == "nominal"
    assert dashboard["objectives_count"] == 3
    assert dashboard["total_hspw"] >= 5.0
    assert "ALFRED PERSONAL OS MASTER DASHBOARD" in dashboard["output"]
    assert "[PERSONAL PRODUCTIVITY & ACADEMICS]" in dashboard["output"]
    assert "[ENGINEERING & WORKFLOW AUTOMATION]" in dashboard["output"]


def test_architecture_layer_compliance_for_kernel():
    """Verify jarvisx.kernel.personal_os aligns strictly under Layer 2 (Alfred) without leaks."""
    assert get_layer_for_module("jarvisx.kernel.personal_os") == "alfred"
    assert get_layer_for_module("jarvisx.kernel") == "alfred"
