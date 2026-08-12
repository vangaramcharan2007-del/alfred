"""Unit & Integration Tests for Phase 1: Observability & Recovery.

Tests:
1. SQLite checkpoint creation, retrieval, and clearance
2. Failure classification across TRANSIENT, RECOVERABLE_REPLAN, PERMISSION_DENIED, FATAL
3. Mission restart/recovery: resumes from checkpoint without re-running earlier completed steps
4. Graceful handling when attempting to resume non-existent checkpoint
5. Full mission lifecycle with automatic checkpoint cleanup upon completion
6. Recovery simulation under mid-execution crash
"""

import os
import shutil
import tempfile
import pytest
from jarvisx.missions.persistence import MissionPersistenceManager
from jarvisx.missions.unified_mission_planner import (
    FailureClassifier,
    MissionPlan,
    MissionStep,
    UnifiedMissionPlanner,
)
from jarvisx.tools.builtin_tools import register_builtin_tools
from jarvisx.tools.tool_kernel import ToolRegistry


class FakeRecoveryLLMRouter:
    """Mock LLMRouter for recovery testing."""
    def __init__(self, responses: list):
        self.responses = responses
        self.call_history = []
        self._index = 0

    def route_request_sync(self, prompt: str, require_offline: bool = False, model_override: str = None):
        self.call_history.append(prompt)
        if self._index < len(self.responses):
            resp = self.responses[self._index]
            self._index += 1
        else:
            resp = "Resumed mission synthesis completed, Sir."
        return {
            "status": "success",
            "provider_id": "fake.local",
            "result": {"status": "AVAILABLE", "response": resp},
        }


@pytest.fixture
def temp_db_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture(autouse=True)
def clean_registry():
    ToolRegistry.reset_instance()
    registry = ToolRegistry.get_instance()
    register_builtin_tools(registry)
    yield registry


def test_failure_classifier_categories():
    """FailureClassifier accurately categorizes various error scenarios."""
    assert FailureClassifier.classify("Permission denied by user") == "PERMISSION_DENIED"
    assert FailureClassifier.classify("Interactive confirmation required") == "PERMISSION_DENIED"
    assert FailureClassifier.classify("Request timed out after 5.0s") == "TRANSIENT"
    assert FailureClassifier.classify("Connection reset by peer") == "TRANSIENT"
    assert FailureClassifier.classify("Page not found 404") == "RECOVERABLE_REPLAN"
    assert FailureClassifier.classify("File missing: notes.txt") == "RECOVERABLE_REPLAN"
    assert FailureClassifier.classify("SyntaxError in code") == "FATAL"


def test_persistence_checkpoints_lifecycle(temp_db_dir):
    """MissionPersistenceManager saves, loads, lists, and clears checkpoints."""
    pm = MissionPersistenceManager(db_dir=temp_db_dir)

    mission_id = "test_mission_001"
    plan_data = {"goal": "Test checkpoint", "steps": []}
    completed = {"step_1": {"time": "10:00 PM"}}

    # Save
    ckpt_id = pm.save_checkpoint(
        mission_id=mission_id,
        goal="Test checkpoint",
        current_step_index=1,
        plan_data=plan_data,
        completed_results=completed,
        status="running",
    )
    assert ckpt_id.startswith("ckpt_test_mission_001")

    # Load
    loaded = pm.load_checkpoint(mission_id)
    assert loaded is not None
    assert loaded["mission_id"] == mission_id
    assert loaded["current_step_index"] == 1
    assert loaded["completed_results"]["step_1"]["time"] == "10:00 PM"

    # List active
    active = pm.list_active_checkpoints()
    assert len(active) == 1
    assert active[0]["mission_id"] == mission_id

    # Clear
    cleared = pm.clear_checkpoint(mission_id)
    assert cleared is True
    assert pm.load_checkpoint(mission_id) is None


def test_resume_mission_recovers_and_completes(temp_db_dir):
    """UnifiedMissionPlanner resumes an interrupted mission from its SQLite checkpoint."""
    pm = MissionPersistenceManager(db_dir=temp_db_dir)
    mission_id = "m_interrupted_99"

    # Simulate a 2-step mission interrupted after Step 1 completed
    plan_data = {
        "goal": "Check time and sysinfo",
        "mission_id": mission_id,
        "steps": [
            {
                "id": "step_1",
                "description": "Get time",
                "tool": "get_current_time",
                "arguments": {},
                "depends_on": [],
                "status": "completed",
                "verified": True,
                "result": {"time": "09:45 PM"},
            },
            {
                "id": "step_2",
                "description": "Get system info",
                "tool": "get_system_info",
                "arguments": {},
                "depends_on": ["step_1"],
                "status": "pending",
                "verified": False,
            },
        ],
    }
    completed_results = {"step_1": {"time": "09:45 PM"}}

    pm.save_checkpoint(
        mission_id=mission_id,
        goal="Check time and sysinfo",
        current_step_index=1,
        plan_data=plan_data,
        completed_results=completed_results,
        status="interrupted",
    )

    fake_router = FakeRecoveryLLMRouter([
        "Resumed successfully and retrieved system info, Sir."
    ])

    planner = UnifiedMissionPlanner(llm_router=fake_router, persistence=pm)
    res = planner.resume_mission(mission_id)

    assert res["status"] == "completed"
    assert res["resumed"] is True
    assert res["completed_count"] == 2
    # Verify step 1 was recovered without re-execution
    recovered_step = next(s for s in res["execution_steps"] if s["step"] == "step_1")
    assert recovered_step.get("recovered") is True
    # Verify step 2 was freshly executed
    step2 = next(s for s in res["execution_steps"] if s["step"] == "step_2")
    assert step2["status"] == "success"
    # Verify checkpoint was cleared upon completion
    assert pm.load_checkpoint(mission_id) is None


def test_resume_non_existent_checkpoint(temp_db_dir):
    """Resuming unknown mission_id returns structured failure without crashing."""
    pm = MissionPersistenceManager(db_dir=temp_db_dir)
    planner = UnifiedMissionPlanner(persistence=pm)
    res = planner.resume_mission("non_existent_mission_xyz")
    assert res["status"] == "failed"
    assert "No active checkpoint found" in res["error"]
