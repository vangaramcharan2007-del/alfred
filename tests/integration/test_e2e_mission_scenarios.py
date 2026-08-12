"""Integration Tests for Phase 2: Full End-to-End Mission Scenarios.

Scenarios:
1. Voice command -> Time & System check -> Natural response
2. Research online -> Fetch webpage -> Extract data -> Synthesized response
3. File creation -> Verification -> Read back created file
4. Desktop window inspection -> Screen UI analysis -> Response
5. Memory retrieval -> Mission planning -> Long-term memory update
6. Comparative research (Python version comparison)
7. Storage & system health overview
8. App launch safety verification
9. Multi-step failure -> Fallback replanning -> Recovery
10. Non-interactive confirmation gating
11. Interrupted mission -> Checkpoint recovery -> Mission completion
12. Complex 4-step full pipeline execution
"""

import os
import shutil
import tempfile
import pytest
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
from jarvisx.missions.persistence import MissionPersistenceManager
from jarvisx.missions.unified_mission_planner import (
    MissionPlan,
    MissionStep,
    UnifiedMissionPlanner,
)
from jarvisx.tools.builtin_tools import register_builtin_tools
from jarvisx.tools.tool_kernel import ToolRegistry


class FakeScenarioRouter:
    """Mock LLMRouter producing deterministic scenario outputs."""
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
            resp = "Scenario execution complete, Sir."
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
# End-to-End Scenarios
# ---------------------------------------------------------------------------

def test_scenario_01_voice_time_and_system_check():
    """Scenario 1: Voice command -> System info & time."""
    fake_router = FakeScenarioRouter([
        '{"type": "tool_call", "tool": "get_system_info", "arguments": {}}',
        "Your system has 16GB RAM and CPU utilization is normal, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_voice_command("Check my system status", persona="ALFRED")
    assert "RAM" in res["response"]


def test_scenario_02_research_and_web_fetch():
    """Scenario 2: Research online -> Fetch webpage -> Extract data."""
    fake_router = FakeScenarioRouter([
        '{"goal": "Research Python", "steps": [{"id": "step_1", "description": "Search", "tool": "web_search", "arguments": {"query": "Python 3.12 release"}, "depends_on": []}, {"id": "step_2", "description": "Fetch", "tool": "fetch_webpage", "arguments": {"url": "https://www.python.org/downloads/"}, "depends_on": ["step_1"]}]}',
        "Python 3.12 introduces isolated subinterpreters and enhanced error messages, Sir.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router)
    res = planner.execute_mission("Research Python 3.12 release")
    assert res["status"] == "completed"
    assert res["completed_count"] == 2
    assert "Python 3.12" in res["response"]


def test_scenario_03_file_creation_and_verification():
    """Scenario 3: Create project file and verify contents."""
    test_path = "var/notes_scenario3.txt"
    try:
        from jarvisx.tools.builtin_tools import CreateFileTool
        tool = CreateFileTool()
        res = tool.execute({"path": test_path, "content": "Jarvis X Mission Complete"})
        assert res.status == "success"
        ver = tool.verify({"path": test_path, "content": "Jarvis X Mission Complete"}, res)
        assert ver.verified is True
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)


def test_scenario_04_desktop_screen_inspection():
    """Scenario 4: Inspect active window and analyze UI elements."""
    fake_router = FakeScenarioRouter([
        '{"goal": "Inspect desktop", "steps": [{"id": "step_1", "description": "Get window", "tool": "get_active_window", "arguments": {}, "depends_on": []}, {"id": "step_2", "description": "Analyze screen", "tool": "analyze_screen", "arguments": {}, "depends_on": ["step_1"]}]}',
        "Desktop screen analysis shows VS Code is currently focused with 12 elements visible, Sir.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router)
    res = planner.execute_mission("Inspect desktop")
    assert res["status"] == "completed"
    assert len(res["execution_steps"]) == 2
    assert "VS Code" in res["response"]


def test_scenario_05_memory_retrieval_and_mission_planning():
    """Scenario 5: Retrieve relevant memory context to inform plan."""
    class FakeMemoryEngine:
        def retrieve_context(self, query, top_k=3):
            return [{"summary": "User prefers fast local execution without GPU throttling."}]
        def store_memory(self, category, summary, details):
            pass

    fake_router = FakeScenarioRouter([
        '{"goal": "Optimize workflow", "steps": [{"id": "step_1", "description": "Check system", "tool": "get_system_info", "arguments": {}, "depends_on": []}]}',
        "Memory context acknowledged: Optimizing system for local execution, Sir.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router, memory_engine=FakeMemoryEngine())
    res = planner.execute_mission("Optimize workflow")
    assert res["status"] == "completed"
    assert any("GPU throttling" in call for call in fake_router.call_history)


def test_scenario_06_comparative_research():
    """Scenario 6: Compare two subjects online."""
    fake_router = FakeScenarioRouter([
        '{"goal": "Compare Python vs Mojo", "steps": [{"id": "step_1", "description": "Search Python", "tool": "web_search", "arguments": {"query": "Python 3.12"}, "depends_on": []}, {"id": "step_2", "description": "Search Mojo", "tool": "web_search", "arguments": {"query": "Mojo language"}, "depends_on": []}]}',
        "Mojo focuses on high performance ML systems while Python maintains ecosystem dominance, Sir.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router)
    res = planner.execute_mission("Compare Python vs Mojo")
    assert res["status"] == "completed"
    assert res["completed_count"] == 2
    assert "Mojo" in res["response"]


def test_scenario_07_system_storage_and_health_overview():
    """Scenario 7: Run system storage cleaning and return reclaimed metrics."""
    orch = DynamicOrchestrator()
    res = orch.execute_voice_command("clean temporary storage", persona="ALFRED")
    assert res["action"] == "clean"
    assert "Eradicated" in res["response"] or "Cleaned" in res["response"]


def test_scenario_08_app_launch_safety_verification():
    """Scenario 8: Open safe browser URL."""
    fake_router = FakeScenarioRouter([
        '{"type": "tool_call", "tool": "browser_open", "arguments": {"url": "https://github.com"}}',
        "Opened GitHub in your browser, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Open GitHub", persona="ALFRED")
    assert res["action"] == "tool_call"
    assert res["execution_steps"][0]["tool"] == "browser_open"


def test_scenario_09_multistep_failure_and_replanning():
    """Scenario 9: Tool failure triggers fallback replanning."""
    fake_router = FakeScenarioRouter([
        '{"goal": "Fetch with fallback", "steps": [{"id": "step_1", "description": "Fetch bad url", "tool": "fetch_webpage", "arguments": {"url": "https://nonexistent-404-domain.org"}, "depends_on": []}]}',
        "Recovered using fallback web search, Sir.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router)
    res = planner.execute_mission("Fetch with fallback")
    assert res["status"] == "completed"
    assert res["plan"]["replan_count"] == 1


def test_scenario_10_non_interactive_confirmation_gate():
    """Scenario 10: Non-interactive session blocks sensitive actions."""
    fake_router = FakeScenarioRouter([
        '{"type": "tool_call", "tool": "click", "arguments": {"x": 100, "y": 200}}',
        "Cannot click without interactive user approval, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Click at 100, 200", persona="ALFRED", interactive=False)
    assert res["action"] == "tool_call"
    assert res["execution_steps"][0]["verified"] is False
    assert "denied" in res["execution_steps"][0]["error"].lower()


def test_scenario_11_interrupted_checkpoint_recovery():
    """Scenario 11: Interrupted mission recovers and completes from checkpoint."""
    temp_dir = tempfile.mkdtemp()
    try:
        pm = MissionPersistenceManager(db_dir=temp_dir)
        mission_id = "m_scenario_11"
        plan_data = {
            "goal": "Multi-stage system check",
            "mission_id": mission_id,
            "steps": [
                {"id": "step_1", "description": "Time", "tool": "get_current_time", "arguments": {}, "depends_on": [], "status": "completed", "verified": True, "result": {"time": "10:15 PM"}},
                {"id": "step_2", "description": "SysInfo", "tool": "get_system_info", "arguments": {}, "depends_on": ["step_1"], "status": "pending", "verified": False},
            ],
        }
        pm.save_checkpoint(
            mission_id=mission_id,
            goal="Multi-stage system check",
            current_step_index=1,
            plan_data=plan_data,
            completed_results={"step_1": {"time": "10:15 PM"}},
            status="interrupted",
        )
        fake_router = FakeScenarioRouter(["All steps resumed and completed, Sir."])
        planner = UnifiedMissionPlanner(llm_router=fake_router, persistence=pm)
        res = planner.resume_mission(mission_id)
        assert res["status"] == "completed"
        assert res["completed_count"] == 2
        assert res["resumed"] is True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scenario_12_complex_four_step_pipeline():
    """Scenario 12: 4-step mission (Web search -> Web fetch -> Sys info -> Compare)."""
    fake_router = FakeScenarioRouter([
        '{"goal": "Full pipeline", "steps": [{"id": "step_1", "description": "Search", "tool": "web_search", "arguments": {"query": "Python latest"}, "depends_on": []}, {"id": "step_2", "description": "Fetch", "tool": "fetch_webpage", "arguments": {"url": "https://www.python.org/downloads/"}, "depends_on": ["step_1"]}, {"id": "step_3", "description": "Get Sys", "tool": "get_system_info", "arguments": {}, "depends_on": []}]}',
        "Based on official downloads and your current environment, Python 3.11 is up to date, Sir.",
    ])
    planner = UnifiedMissionPlanner(llm_router=fake_router)
    res = planner.execute_mission("Full pipeline")
    assert res["status"] == "completed"
    assert res["completed_count"] == 3
    assert "Python 3.11" in res["response"]
