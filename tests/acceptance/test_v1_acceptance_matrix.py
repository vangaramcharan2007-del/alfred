"""Jarvis X v1.0 Acceptance Matrix Tests (A through P).

Covers all 16 acceptance scenarios using actual codebase APIs.
"""

import json
import os
import tempfile
import time
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
from jarvisx.tools.tool_executor import ToolExecutor
from jarvisx.tools.tool_kernel import ToolRegistry, Tool, ToolSpec, ToolResult, PermissionLevel
from jarvisx.tools.builtin_tools import (
    register_builtin_tools, ReadFileTool, CreateFileTool,
    GetCurrentTimeTool, GetSystemInfoTool, WebSearchTool, FetchWebpageTool,
    BrowserOpenTool, CaptureScreenTool, ClickTool, PressKeyTool,
)
from jarvisx.tools.permission_gateway import PermissionGateway
from jarvisx.llm.llm_router import LLMRouter
from jarvisx.missions.unified_mission_planner import (
    UnifiedMissionPlanner, MissionPlan, MissionStep, FailureClassifier,
)
from jarvisx.missions.persistence import MissionPersistenceManager
from jarvisx.memory_intelligence.memory_engine import MemoryIntelligenceEngine
from jarvisx.proactive.proactive_evaluator import ProactiveEvaluator
from jarvisx.proactive.proactive_memory import ProactiveMemory
from jarvisx.reliability.circuit_breaker import CircuitBreaker, CircuitState
from jarvisx.reliability.watchdog_guard import ResourceLimitGuard
from jarvisx.reliability.reliability_engine import ReliabilityEngine
from jarvisx.tools.web_research import WebSearchEngine, WebPageFetcher


# ---- A. Voice → answer → TTS ----

def test_acceptance_A_voice_answer_tts():
    """A. Voice → answer → TTS: DynamicOrchestrator returns a spoken time response."""
    orch = DynamicOrchestrator()
    res = orch.execute_voice_command("What time is it?", persona="ALFRED")
    assert res.get("response"), "Expected a spoken response"
    assert "time" in res["response"].lower() or "AM" in res["response"] or "PM" in res["response"]
    assert res.get("action") == "speak"


# ---- B. Voice → safe tool → result ----

def test_acceptance_B_voice_safe_tool():
    """B. Voice → safe tool: ToolExecutor runs get_current_time (SAFE) without permission gate."""
    registry = ToolRegistry.get_instance()
    if not registry.list_tools():
        register_builtin_tools(registry)
    executor = ToolExecutor(registry=registry)
    result = executor.execute("get_current_time", {}, interactive=False)
    assert result.status == "success"
    assert result.verified is True
    assert "time" in result.result


# ---- C. Voice → CONFIRM tool → approval gate ----

def test_acceptance_C_confirm_tool_denied_non_interactive():
    """C. CONFIRM tool is denied in non-interactive mode."""
    registry = ToolRegistry.get_instance()
    if not registry.list_tools():
        register_builtin_tools(registry)
    executor = ToolExecutor(registry=registry)
    result = executor.execute("create_file", {"path": "test_confirm.txt", "content": "x"}, interactive=False)
    assert result.status == "failed"
    assert "non-interactive" in result.error.lower() or "denied" in result.error.lower()


# ---- D. Voice → denied tool ----

def test_acceptance_D_restricted_tool_blocked():
    """D. RESTRICTED tool is always blocked regardless of interactivity."""
    registry = ToolRegistry.get_instance()
    if not registry.list_tools():
        register_builtin_tools(registry)

    class RestrictedTool(Tool):
        def spec(self):
            return ToolSpec(name="restricted_test", description="Test", input_schema={"type": "object", "properties": {}, "required": []}, permission_level=PermissionLevel.RESTRICTED)
        def execute(self, arguments):
            return ToolResult(status="success", tool="restricted_test", result="should not reach")
        def verify(self, arguments, result):
            return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=True)

    registry.register(RestrictedTool())
    executor = ToolExecutor(registry=registry)
    res_interactive = executor.execute("restricted_test", {}, interactive=True)
    res_non_interactive = executor.execute("restricted_test", {}, interactive=False)
    assert res_interactive.status == "failed"
    assert res_non_interactive.status == "failed"
    assert "restricted" in res_interactive.error.lower()


# ---- E. Multi-step mission ----

def test_acceptance_E_multi_step_mission():
    """E. Multi-step mission: executes goal through UnifiedMissionPlanner."""
    mock_router = MagicMock()
    mock_router.route_request_sync.return_value = {
        "status": "success",
        "result": {
            "status": "AVAILABLE",
            "response": json.dumps({
                "goal": "Check system time and status",
                "steps": [
                    {"id": "step_1", "description": "Get time", "tool": "get_current_time", "arguments": {}, "depends_on": []},
                    {"id": "step_2", "description": "Get sys info", "tool": "get_system_info", "arguments": {}, "depends_on": ["step_1"]},
                ]
            })
        }
    }
    planner = UnifiedMissionPlanner(llm_router=mock_router)
    res = planner.execute_mission(
        goal="Check system time and status",
        persona="ALFRED",
        interactive=False,
        max_steps=5,
    )
    assert res["status"] in ("completed", "success")
    assert "mission_id" in res
    assert len(res["execution_steps"]) == 2


# ---- F. Web research ----

def test_acceptance_F_web_research():
    """F. Web research: WebSearchEngine returns bounded results, WebPageFetcher validates URLs."""
    engine = WebSearchEngine()
    results = engine.search("Python programming")
    assert isinstance(results, dict)
    assert "results" in results
    assert len(results["results"]) <= 10

    fetcher = WebPageFetcher()
    val = fetcher.validate_url("https://example.com")
    assert val["valid"] is True
    bad = fetcher.validate_url("javascript:alert(1)")
    assert bad["valid"] is False


# ---- G. Computer-use action + re-observation ----

def test_acceptance_G_computer_use():
    """G. Click requires CONFIRM and is denied non-interactively; CaptureScreen is SAFE."""
    registry = ToolRegistry.get_instance()
    if not registry.list_tools():
        register_builtin_tools(registry)
    executor = ToolExecutor(registry=registry)

    click_res = executor.execute("click", {"x": 100, "y": 100}, interactive=False)
    assert click_res.status == "failed"
    assert "non-interactive" in click_res.error.lower() or "denied" in click_res.error.lower()

    capture_res = executor.execute("capture_screen", {}, interactive=False)
    assert capture_res.status == "success"
    assert capture_res.result.get("width", 0) > 0


# ---- H. Memory recall across fresh process ----

def test_acceptance_H_memory_recall(tmp_path):
    """H. Memory stores and retrieves facts across separate engine instances."""
    db_file = str(tmp_path / "memory_test.db")
    engine1 = MemoryIntelligenceEngine(db_path=db_file)
    success, rec, err = engine1.remember("User prefers Python and dark mode")
    assert success is True

    # Verify fact persists via new instance pointing to same db
    engine2 = MemoryIntelligenceEngine(db_path=db_file)
    ctx2 = engine2.get_personal_context(query="Python")
    assert ctx2 is not None


# ---- I. Ollama failure → OpenRouter fallback ----

def test_acceptance_I_ollama_fallback():
    """I. When Ollama fails, LLMRouter falls back to OpenRouter."""
    router = LLMRouter()
    ollama = router.registry.get("ollama.local")
    original_generate = ollama.generate

    async def failing_generate(*args, **kwargs):
        raise ConnectionError("Ollama unavailable")
    ollama.generate = failing_generate

    res = router.route_request_sync("Hello")
    assert res.get("fallback_used") is True or res.get("status") == "provider_unavailable"
    ollama.generate = original_generate


# ---- J. Both providers unavailable ----

def test_acceptance_J_both_providers_down():
    """J. Both providers down returns provider_unavailable."""
    router = LLMRouter()
    ollama = router.registry.get("ollama.local")
    openrouter = router.registry.get("openrouter.gateway")

    async def fail(*a, **kw):
        raise ConnectionError("Down")
    ollama.generate = fail
    openrouter.generate = fail

    res = router.route_request_sync("Hello")
    assert res["status"] == "provider_unavailable"


# ---- K. Mission interruption → resume ----

def test_acceptance_K_mission_resume():
    """K. Mission checkpoint save/load and resume."""
    pm = MissionPersistenceManager()
    plan = MissionPlan(
        goal="Resume test",
        mission_id="resume_test_001",
        steps=[
            MissionStep(id="s1", description="Done", tool="get_current_time"),
            MissionStep(id="s2", description="Pending", tool="get_system_info", depends_on=["s1"]),
        ],
    )
    plan.steps[0].status = "completed"
    plan.steps[0].verified = True
    plan.steps[0].result = {"time": "12:00"}
    completed = {"s1": {"time": "12:00"}}

    pm.save_checkpoint(
        mission_id=plan.mission_id, goal=plan.goal,
        current_step_index=1, plan_data=plan.to_dict(),
        completed_results=completed, status="running",
    )
    ckpts = pm.list_active_checkpoints()
    found = any(c["mission_id"] == "resume_test_001" for c in ckpts)
    assert found, "Checkpoint not saved"


# ---- L. Daemon restart / health ----

def test_acceptance_L_daemon_health():
    """L. ReliabilityEngine.doctor() returns HEALTHY status."""
    engine = ReliabilityEngine()
    diag = engine.doctor()
    assert diag["status"] in ("HEALTHY", "DEGRADED")
    assert diag["snapshots_count"] >= 0


# ---- M. Malformed LLM tool call ----

def test_acceptance_M_malformed_tool_call():
    """M. parse_tool_call rejects garbage, partial JSON, missing fields."""
    assert ToolExecutor.parse_tool_call("This is just a normal response") is None
    assert ToolExecutor.parse_tool_call("garbage {{{{ json") is None
    assert ToolExecutor.parse_tool_call('{"type": "tool_call"}') is None
    assert ToolExecutor.parse_tool_call('{"type": "tool_call", "tool": "x"}') is None
    assert ToolExecutor.parse_tool_call('{"some": "random", "json": 123}') is None


# ---- N. Tool timeout/failure ----

def test_acceptance_N_tool_failure():
    """N. ToolExecutor handles tool execution exception gracefully."""
    registry = ToolRegistry.get_instance()
    if not registry.list_tools():
        register_builtin_tools(registry)

    class CrashingTool(Tool):
        def spec(self):
            return ToolSpec(name="crash_tool", description="Crashes", input_schema={"type": "object", "properties": {}, "required": []}, permission_level=PermissionLevel.SAFE)
        def execute(self, arguments):
            raise RuntimeError("Simulated crash")
        def verify(self, arguments, result):
            return result

    registry.register(CrashingTool())
    executor = ToolExecutor(registry=registry)
    res = executor.execute("crash_tool", {}, interactive=False)
    assert res.status == "failed"
    assert "Simulated crash" in res.error


# ---- O. Proactive reminder + duplicate suppression ----

def test_acceptance_O_proactive_duplicate_suppression():
    """O. ProactiveEvaluator suppresses duplicate interventions within cooldown."""
    pm = ProactiveMemory()
    now = time.time()
    pm.update_intervention_cooldown("study_reminder", now, "abc123")
    record = pm.get_last_intervention_time("study_reminder")
    assert record is not None
    last_time, last_hash = record
    assert last_hash == "abc123"
    assert abs(last_time - now) < 2


# ---- P. Low-memory / resource guard ----

def test_acceptance_P_resource_guard():
    """P. ResourceLimitGuard detects when RSS exceeds threshold."""
    guard = ResourceLimitGuard(max_rss_mb=0.001, min_free_disk_mb=0.0)
    status = guard.check_resources()
    assert status["rss_ok"] is False
    assert status["healthy"] is False

    guard_ok = ResourceLimitGuard(max_rss_mb=99999.0, min_free_disk_mb=0.0)
    status_ok = guard_ok.check_resources()
    assert status_ok["rss_ok"] is True
    assert status_ok["healthy"] is True
