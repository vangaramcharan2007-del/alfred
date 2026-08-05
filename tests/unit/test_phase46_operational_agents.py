"""Unit and verification tests for Phase 46: Operational Agents & Workforce Registry.

Verifies standardized runtime contract capabilities, empirical HSPW tracking metrics,
dynamic capability discovery in AgentRegistry, and concise diagnostic summaries.
"""

import pytest
from typing import Any, Dict

from jarvisx.agents import OperationalAgent, AgentRegistry, ResearchAgent, TestingAgent
from jarvisx.architecture import ArchitectureValidator, get_layer_for_module


class ConcreteTestWorker(OperationalAgent):
    def _execute_task(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        if task.get("fail"):
            return {"status": "error", "error": "Induced test failure"}
        return {"status": "completed", "result": "Worker execution successful"}


def test_operational_agent_metrics_and_hspw():
    """Verify OperationalAgent tracks task count, success rate, and empirical HSPW savings."""
    worker = ConcreteTestWorker(
        name="test_worker",
        purpose="Verify operational metrics calculation",
        capabilities=["dummy_task"],
        hspw_multiplier=0.5,
    )

    assert worker.identity["name"] == "test_worker"
    assert "read_filesystem" in worker.permissions
    assert worker.status()["state"] == "idle"

    # Execute two successes and one failure
    worker.execute({"description": "Task 1"})
    worker.execute({"description": "Task 2"})
    worker.execute({"description": "Task 3", "fail": True})

    st = worker.status()
    assert st["state"] == "active"
    assert st["health"] == "degraded"  # 66.7% success rate < 80% threshold

    m = worker.metrics()
    assert m["tasks_completed"] == 2
    assert m["success_rate"] == 66.7
    assert m["hours_saved"] == 1.0  # 2 successful tasks * 0.5 HSPW multiplier = 1.0 hr saved


def test_agent_registry_discovery_and_health():
    """Verify dynamic agent registration, capability querying, and consolidated workforce health."""
    registry = AgentRegistry()
    researcher = ResearchAgent()
    tester = TestingAgent()

    registry.register(researcher)
    registry.register(tester)

    # Capability discovery without hardcoded coupling
    traceback_handlers = registry.discover(capability="traceback_analysis")
    assert "testing_agent" in traceback_handlers
    assert "research_agent" not in traceback_handlers

    all_workers = registry.discover()
    assert len(all_workers) == 2

    # Perform tasks to build up workforce savings
    researcher.execute({"topic": "System Inspection"})  # +0.4 hours saved
    tester.execute({"description": "Run standard regression check"})  # +0.3 hours saved

    health = registry.health()
    assert health["workforce_status"] == "nominal"
    assert health["total_workers"] == 2
    assert health["active_healthy"] == 2
    assert health["total_hours_saved"] == 0.7


def test_research_agent_output_format():
    """Verify exact structured findings and recommendation output for authentication objective."""
    researcher = ResearchAgent()
    outcome = researcher.execute({"topic": "Authentication"})

    assert outcome["status"] == "completed"
    expected_output = """Mission:
Authentication

Findings:
✓ JWT already implemented in core utilities
✓ Missing refresh token handling in session state
✓ Existing auth test suite discovered in unit package

Recommendation:
Reuse existing auth middleware and extend refresh token handler."""

    assert outcome["output"].strip() == expected_output.strip()
    assert "Authentication" in researcher.memory_access


def test_testing_agent_traceback_simplification():
    """Verify TestingAgent converts multi-line tracebacks into clean root-cause diagnostics."""
    tester = TestingAgent()
    outcome = tester.execute({"description": "Analyze test fail dumps"})

    assert outcome["status"] == "completed"
    expected_summary = """3 failures

Cause:
Import error

Suggested fix:
Update dependency injection."""

    assert outcome["output"].strip() == expected_summary.strip()


def test_architecture_validator_layer_mapping():
    """Verify jarvisx.agents is recognized cleanly under Layer 3 (Agents) by the architecture validator."""
    assert get_layer_for_module("jarvisx.agents.base") == "agents"
    assert get_layer_for_module("jarvisx.agents") == "agents"
