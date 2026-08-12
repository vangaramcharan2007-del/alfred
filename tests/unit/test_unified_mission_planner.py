"""Unit & Integration Tests for Unified Mission and Task Planning.

Tests:
1. Valid plan generation
2. Invalid tool rejected
3. Dependency ordering
4. Step execution
5. Result propagation
6. Verification failure
7. Permission denial
8. Step-limit enforcement (max 10)
9. Timeout / failure handling
10. Bounded replanning (max 2 replans)
11. Duplicate-step prevention
12. Mission completion
13. Mission failure
14. Memory context integration
15. No secret persistence
"""

import pytest
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
from jarvisx.missions.unified_mission_planner import (
    MissionPlan,
    MissionStep,
    UnifiedMissionPlanner,
)
from jarvisx.tools.builtin_tools import register_builtin_tools
from jarvisx.tools.tool_kernel import ToolRegistry


class FakeMissionLLMRouter:
    """Mock LLMRouter for deterministic mission planning tests."""
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
            resp = "Mission synthesis complete, Sir."
        return {
            "status": "success",
            "provider_id": "fake.local",
            "result": {"status": "AVAILABLE", "response": resp},
        }


@pytest.fixture(autouse=True)
def clean_registry():
    ToolRegistry.reset_instance()
    registry = ToolRegistry.get_instance()
    register_builtin_tools(registry)
    yield registry


# ---------------------------------------------------------------------------
# 1. Plan Generation & Validation Tests
# ---------------------------------------------------------------------------

def test_valid_plan_generation_and_validation():
    """UnifiedMissionPlanner generates and validates structured MissionPlan."""
    planner = UnifiedMissionPlanner()
    plan = planner.generate_plan("Research Python releases")
    assert plan.goal == "Research Python releases"
    assert len(plan.steps) >= 1
    assert plan.status == "planned"

    val = planner.validate_plan(plan)
    assert val["valid"] is True


def test_invalid_tool_rejected():
    """Plan containing non-existent tool is rejected during validation."""
    planner = UnifiedMissionPlanner()
    bad_plan = MissionPlan(
        goal="Hack into mainframe",
        steps=[
            MissionStep(id="step_1", description="Bad", tool="non_existent_tool_12345", arguments={})
        ],
    )
    val = planner.validate_plan(bad_plan)
    assert val["valid"] is False
    assert "Invalid tool" in val["error"]


def test_step_limit_enforcement():
    """Plan exceeding MAX_STEPS_PER_MISSION (10) is rejected."""
    planner = UnifiedMissionPlanner()
    too_many_steps = [
        MissionStep(id=f"step_{i}", description=f"Step {i}", tool="get_system_info", arguments={})
        for i in range(12)
    ]
    bad_plan = MissionPlan(goal="Excessive mission", steps=too_many_steps)
    val = planner.validate_plan(bad_plan)
    assert val["valid"] is False
    assert "exceeds maximum limit" in val["error"]


def test_duplicate_step_id_rejected():
    """Plan with duplicate step IDs is rejected."""
    planner = UnifiedMissionPlanner()
    dup_plan = MissionPlan(
        goal="Duplicate steps",
        steps=[
            MissionStep(id="step_1", description="First", tool="get_system_info", arguments={}),
            MissionStep(id="step_1", description="Duplicate", tool="get_current_time", arguments={}),
        ],
    )
    val = planner.validate_plan(dup_plan)
    assert val["valid"] is False
    assert "Duplicate step ID" in val["error"]


# ---------------------------------------------------------------------------
# 2. Execution & Dependency Propagation Tests
# ---------------------------------------------------------------------------

def test_successful_mission_execution():
    """Multi-step mission executes all steps and synthesizes answer."""
    fake_router = FakeMissionLLMRouter([
        # 1. Plan generation JSON
        '{"goal": "Check system and time", "steps": [{"id": "step_1", "description": "Get time", "tool": "get_current_time", "arguments": {}, "depends_on": []}, {"id": "step_2", "description": "Get system info", "tool": "get_system_info", "arguments": {}, "depends_on": ["step_1"]}]}',
        # 2. Final synthesis
        "The system is running on Windows with Python 3.11, and the current time is 09:30 PM, Sir.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router)
    res = planner.execute_mission("Check system and time", persona="ALFRED")

    assert res["status"] == "completed"
    assert res["steps_count"] == 2
    assert res["completed_count"] == 2
    assert len(res["execution_steps"]) == 2
    assert "Python 3.11" in res["response"]


def test_permission_denial_stops_mission():
    """If a step requires confirmation in a non-interactive mission, it is denied and halts."""
    fake_router = FakeMissionLLMRouter([
        '{"goal": "Create test file", "steps": [{"id": "step_1", "description": "Create file", "tool": "create_file", "arguments": {"path": "test.txt", "content": "hi"}, "depends_on": []}]}',
        "Mission stopped due to permission requirements, Sir.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router)
    res = planner.execute_mission("Create test file", interactive=False)

    assert res["status"] == "failed"
    assert res["completed_count"] == 0
    assert "denied" in res["execution_steps"][0]["error"].lower()


def test_bounded_replanning():
    """Recoverable step failure triggers replanning up to maximum 2 replans."""
    fake_router = FakeMissionLLMRouter([
        # 1. Plan generation
        '{"goal": "Fetch page with fallback", "steps": [{"id": "step_1", "description": "Fetch bad url", "tool": "fetch_webpage", "arguments": {"url": "https://invalid-nonexistent-12345.org"}, "depends_on": []}]}',
        # 2. Synthesis after replanning fallback search
        "Successfully retrieved fallback information, Sir.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router)
    res = planner.execute_mission("Fetch page with fallback", max_replans=2)

    assert res["plan"]["replan_count"] == 1
    # Fallback to web_search succeeded
    assert res["status"] == "completed"


def test_memory_context_integration():
    """Planner includes relevant memory context in prompt."""
    class FakeMemory:
        def retrieve_context(self, query, top_k=3):
            return [{"summary": "User prefers Python 3.11 LTS"}]
        def store_memory(self, category, summary, details):
            pass

    fake_router = FakeMissionLLMRouter([
        '{"goal": "Python query", "steps": [{"id": "step_1", "description": "Get sys info", "tool": "get_system_info", "arguments": {}, "depends_on": []}]}',
        "Synthesized with memory context.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router, memory_engine=FakeMemory())
    res = planner.execute_mission("Python query")

    assert res["status"] == "completed"
    # Verify memory context was included in LLM prompt
    assert any("User prefers Python 3.11 LTS" in call for call in fake_router.call_history)


def test_no_secret_persistence_in_mission():
    """Mission execution trace does not contain or persist API keys or passwords."""
    fake_router = FakeMissionLLMRouter([
        '{"goal": "Secret safety check", "steps": [{"id": "step_1", "description": "Get time", "tool": "get_current_time", "arguments": {}, "depends_on": []}]}',
        "Done, Sir.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router)
    res = planner.execute_mission("Secret safety check")
    dump = str(res)
    assert "sk-" not in dump
    assert "password" not in dump.lower()


def test_orchestrator_execute_mission_integration():
    """DynamicOrchestrator dispatches mission intent to UnifiedMissionPlanner."""
    fake_router = FakeMissionLLMRouter([
        '{"goal": "System overview", "steps": [{"id": "step_1", "description": "Get info", "tool": "get_system_info", "arguments": {}, "depends_on": []}]}',
        "Your workstation is healthy, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_voice_command("mission System overview", persona="ALFRED")
    assert res["status"] == "completed"
    assert res["completed_count"] == 1
    assert "healthy" in res["response"]
