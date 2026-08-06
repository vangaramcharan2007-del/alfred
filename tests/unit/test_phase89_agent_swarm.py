"""Unit and Integration Tests for Phase 89: Autonomous Personal AI Agent Swarm & Delegation Mesh.

Tests AgentSwarmEngine parallel micro-worker dispatching, result aggregation, and kernel objectives.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.agents import AgentSwarmEngine, MicroAgentWorker


def test_agent_swarm_engine_dispatch():
    """Verify AgentSwarmEngine load balances subtasks across specialized micro-worker agents."""
    swarm = AgentSwarmEngine()
    assert len(swarm.workers) == 5

    subtasks = [
        {"domain": "CODING", "action": "refactor_auth_module"},
        {"domain": "ACADEMIC", "action": "synthesize_lecture_notes"},
        {"domain": "DEVOPS", "action": "deploy_staging_container"},
    ]

    res = swarm.dispatch_swarm_mission(
        mission_objective="Prepare production release build",
        subtasks=subtasks,
        os_kernel=None,
    )

    assert res["status"] == "SWARM_COMPLETED"
    assert res["subtasks_count"] == 3
    assert len(res["results"]) == 3
    assert res["swarm_hspw"] >= 18.5


def test_kernel_objective_routing_phase89():
    """Verify PersonalOSKernel routes agent swarm mission delegation objectives."""
    kernel = PersonalOSKernel()

    res = kernel.execute_objective("swarm dispatch")
    assert res["status"] == "SWARM_COMPLETED"
    assert res["active_workers"] >= 5
