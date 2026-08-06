"""Unit and Integration Tests for Phase 81: Zero-Touch PC Workflow Orchestration & Autopilot.

Tests WorkflowAutopilotEngine macro sequences and kernel objective handlers.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.execution import WorkflowAutopilotEngine


def test_workflow_autopilot_engine_workflows():
    """Verify WorkflowAutopilotEngine returns registered macro sequences and executes composite steps."""
    kernel = PersonalOSKernel()
    engine = WorkflowAutopilotEngine()

    wf_dict = engine.get_available_workflows()
    assert "ML_STUDY_SESSION" in wf_dict
    assert "SYSTEM_DEEP_CLEAN" in wf_dict
    assert "PROJECT_BOOTSTRAP" in wf_dict

    res = engine.execute_autopilot_workflow("SYSTEM_DEEP_CLEAN", os_kernel=kernel)
    assert res["status"] == "COMPLETED"
    assert res["workflow"] == "SYSTEM_DEEP_CLEAN"
    assert res["steps_executed"] >= 3
    assert res["autopilot_hspw"] >= 12.5


def test_kernel_objective_routing_phase81():
    """Verify PersonalOSKernel routes autopilot workflow objectives."""
    kernel = PersonalOSKernel()

    ap_res = kernel.execute_objective("prepare machine", workflow="ML_STUDY_SESSION")
    assert ap_res["status"] == "COMPLETED"
    assert ap_res["workflow"] == "ML_STUDY_SESSION"

    dc_res = kernel.execute_objective("deep clean workflow", workflow="SYSTEM_DEEP_CLEAN")
    assert dc_res["status"] == "COMPLETED"
    assert dc_res["workflow"] == "SYSTEM_DEEP_CLEAN"
