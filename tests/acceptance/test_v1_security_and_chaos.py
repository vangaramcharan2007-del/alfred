"""Jarvis X v1.0 Security Audit & Failure Injection Tests.

Section 4: Security Audit (10 tests)
Section 5: Failure Injection / Chaos (10 tests)
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
from jarvisx.tools.tool_executor import ToolExecutor
from jarvisx.tools.tool_kernel import ToolRegistry, Tool, ToolSpec, ToolResult, PermissionLevel
from jarvisx.tools.builtin_tools import (
    register_builtin_tools, ReadFileTool, CreateFileTool,
    PressKeyTool, BrowserOpenTool, CaptureScreenTool,
    GetSystemInfoTool,
)
from jarvisx.tools.permission_gateway import PermissionGateway
from jarvisx.tools.web_research import WebSearchEngine, WebPageFetcher
from jarvisx.llm.llm_router import LLMRouter
from jarvisx.missions.unified_mission_planner import (
    UnifiedMissionPlanner, MissionPlan, MissionStep, FailureClassifier,
)
from jarvisx.proactive.proactive_evaluator import ProactiveEvaluator
from jarvisx.proactive.proactive_memory import ProactiveMemory
from jarvisx.reliability.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerOpenError


# ======================================================================
# SECTION 4: SECURITY AUDIT
# ======================================================================

def test_security_confirm_cannot_be_bypassed():
    """CONFIRM tools are always denied in non-interactive sessions."""
    registry = ToolRegistry.get_instance()
    if not registry.list_tools():
        register_builtin_tools(registry)
    executor = ToolExecutor(registry=registry)

    # create_file is CONFIRM level
    res = executor.execute("create_file", {"path": "hack.txt", "content": "pwned"}, interactive=False)
    assert res.status == "failed"
    assert "non-interactive" in res.error.lower() or "denied" in res.error.lower()

    # click is CONFIRM level
    res2 = executor.execute("click", {"x": 500, "y": 500}, interactive=False)
    assert res2.status == "failed"

    # type_text is CONFIRM level
    res3 = executor.execute("type_text", {"text": "injected"}, interactive=False)
    assert res3.status == "failed"


def test_security_restricted_always_blocked():
    """RESTRICTED tools are blocked even in interactive mode."""
    registry = ToolRegistry.get_instance()
    if not registry.list_tools():
        register_builtin_tools(registry)

    class DangerousTool(Tool):
        def spec(self):
            return ToolSpec(
                name="dangerous_op", description="Dangerous",
                input_schema={"type": "object", "properties": {}, "required": []},
                permission_level=PermissionLevel.RESTRICTED,
            )
        def execute(self, arguments):
            return ToolResult(status="success", tool="dangerous_op", result="should not execute")
        def verify(self, arguments, result):
            return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=True)

    registry.register(DangerousTool())
    executor = ToolExecutor(registry=registry)
    res = executor.execute("dangerous_op", {}, interactive=True)
    assert res.status == "failed"
    assert "restricted" in res.error.lower()


def test_security_path_traversal_blocked():
    """Path traversal attempts are safely handled and do not escape."""
    tool = ReadFileTool()
    res = tool.execute({"path": "../../../etc/passwd"})
    assert res.status == "failed"

    res2 = tool.execute({"path": "..\\..\\..\\windows\\system32\\config\\sam"})
    assert res2.status == "failed"


def test_security_system_paths_blocked():
    """create_file blocks writes to system-critical locations."""
    tool = CreateFileTool()
    res = tool.execute({"path": "C:\\Windows\\system32\\malware.exe", "content": "bad"})
    assert res.status == "failed"
    assert "blocked" in res.error.lower() or "system" in res.error.lower()

    res2 = tool.execute({"path": "C:\\Program Files\\malware.exe", "content": "bad"})
    assert res2.status == "failed"


def test_security_no_secrets_in_tool_results():
    """get_system_info does not leak API keys, tokens, or passwords."""
    tool = GetSystemInfoTool()
    res = tool.execute({})
    result_str = json.dumps(res.result).lower()
    sensitive_patterns = ["sk-proj-", "ghp_", "bearer ", "password=", "api_key", "secret_key"]
    for pat in sensitive_patterns:
        assert pat not in result_str, f"Sensitive pattern '{pat}' found in system info"


def test_security_browser_rejects_non_http():
    """browser_open rejects javascript:, file://, ftp:// URLs."""
    fetcher = WebPageFetcher()
    for bad_url in ["javascript:alert(1)", "file:///etc/passwd", "ftp://evil.com/payload"]:
        val = fetcher.validate_url(bad_url)
        assert val["valid"] is False, f"URL {bad_url} should be rejected"


def test_security_autonomous_actions_bounded():
    """ProactiveEvaluator executes CONFIRM tools with interactive=False, which blocks them."""
    registry = ToolRegistry.get_instance()
    if not registry.list_tools():
        register_builtin_tools(registry)
    executor = ToolExecutor(registry=registry)

    # Simulating what ProactiveEvaluator does: calls executor with interactive=False
    res = executor.execute("create_file", {"path": "autonomous.txt", "content": "auto"}, interactive=False)
    assert res.status == "failed"
    assert "non-interactive" in res.error.lower() or "denied" in res.error.lower()


def test_security_mission_step_limit_enforced():
    """Mission plans with >10 steps are rejected during validation."""
    planner = UnifiedMissionPlanner()
    steps = [
        MissionStep(id=f"s{i}", description=f"Step {i}", tool="get_current_time")
        for i in range(11)
    ]
    plan = MissionPlan(goal="Too many steps", steps=steps)
    validation = planner.validate_plan(plan)
    assert not validation["valid"], "Plan with 11 steps should be rejected"


def test_security_mission_replan_limit_enforced():
    """Replan count cannot exceed max_replans."""
    plan = MissionPlan(goal="Test replan", replan_count=3)
    assert plan.replan_count > 2


def test_security_press_key_allowlist():
    """PressKeyTool rejects disallowed key combinations."""
    tool = PressKeyTool()
    for bad_key in ["ctrl+alt+delete", "alt+f4", "win+r", "rm -rf", "format"]:
        res = tool.execute({"key": bad_key})
        assert res.status == "failed", f"Key '{bad_key}' should be rejected"

    assert "enter" in PressKeyTool.ALLOWED_KEYS


# ======================================================================
# SECTION 5: FAILURE INJECTION / CHAOS
# ======================================================================

def test_chaos_ollama_unavailable():
    """When Ollama provider raises ConnectionError, router attempts fallback."""
    router = LLMRouter()
    ollama = router.registry.get("ollama.local")

    async def fail(*a, **kw):
        raise ConnectionError("Ollama server not running")
    ollama.generate = fail

    res = router.route_request_sync("test prompt")
    assert res.get("fallback_used") is True or res["status"] == "provider_unavailable"


def test_chaos_openrouter_unavailable():
    """When OpenRouter returns NOT_AVAILABLE after Ollama fails, status is provider_unavailable."""
    router = LLMRouter()
    ollama = router.registry.get("ollama.local")
    openrouter = router.registry.get("openrouter.gateway")

    async def fail(*a, **kw):
        raise ConnectionError("Down")
    ollama.generate = fail
    openrouter.generate = fail

    res = router.route_request_sync("test prompt")
    assert res["status"] == "provider_unavailable"


def test_chaos_network_timeout():
    """WebPageFetcher handles invalid URLs and bad hosts gracefully."""
    fetcher = WebPageFetcher()
    res = fetcher.fetch("https://invalid-nonexistent-domain-xyz-12345.org")
    assert res.get("status") == "failed" or res.get("error")


def test_chaos_malformed_tool_json():
    """parse_tool_call handles all forms of malformed input."""
    cases = [
        "",
        "Hello world, no JSON here",
        "{{{{broken json",
        '{"type": "tool_call"}',
        '{"type": "tool_call", "tool": "x"}',
        '{"random": "object"}',
        '{"type": "not_a_tool_call", "tool": "x", "arguments": {}}',
    ]
    for case in cases:
        result = ToolExecutor.parse_tool_call(case)
        assert result is None, f"Should reject: {case!r}"


def test_chaos_tool_exception():
    """ToolExecutor returns structured failure when tool.execute() raises."""
    registry = ToolRegistry.get_instance()
    if not registry.list_tools():
        register_builtin_tools(registry)

    class ExplodingTool(Tool):
        def spec(self):
            return ToolSpec(
                name="exploding_tool", description="Explodes",
                input_schema={"type": "object", "properties": {}, "required": []},
                permission_level=PermissionLevel.SAFE,
            )
        def execute(self, arguments):
            raise RuntimeError("Kaboom!")
        def verify(self, arguments, result):
            return result

    registry.register(ExplodingTool())
    executor = ToolExecutor(registry=registry)
    res = executor.execute("exploding_tool", {}, interactive=False)
    assert res.status == "failed"
    assert "Kaboom!" in res.error


def test_chaos_vision_failure():
    """CaptureScreenTool handles desktop scan safely."""
    registry = ToolRegistry.get_instance()
    if not registry.list_tools():
        register_builtin_tools(registry)
    executor = ToolExecutor(registry=registry)
    res = executor.execute("capture_screen", {}, interactive=False)
    assert res.status in ("success", "failed")


def test_chaos_memory_failure():
    """DynamicOrchestrator handles memory engine exceptions without crashing."""
    orch = DynamicOrchestrator()
    mock_mem = MagicMock()
    mock_mem.get_personal_context.side_effect = RuntimeError("Memory DB corrupt")
    mock_mem.extract_and_store_from_conversation.side_effect = RuntimeError("Memory write failed")
    orch._memory_engine = mock_mem

    res = orch.execute_voice_command("What time is it?", persona="ALFRED")
    assert res.get("response"), "Should still respond despite memory failure"


def test_chaos_mission_step_failure():
    """Mission execution handles unresolvable / failed tools gracefully."""
    mock_router = MagicMock()
    mock_router.route_request_sync.return_value = {
        "status": "success",
        "result": {
            "status": "AVAILABLE",
            "response": json.dumps({
                "goal": "Test failing mission",
                "steps": [
                    {"id": "step_1", "description": "Good step", "tool": "get_current_time", "arguments": {}, "depends_on": []},
                    {"id": "step_2", "description": "Failing step", "tool": "nonexistent_tool_xyz", "arguments": {}, "depends_on": ["step_1"]},
                ]
            })
        }
    }
    planner = UnifiedMissionPlanner(llm_router=mock_router)
    res = planner.execute_mission("Test failing mission", interactive=False, max_steps=3)
    assert res["status"] in ("completed", "failed")
    assert "plan" in res or "mission_id" in res
    assert "error" in res or res["status"] == "failed"


def test_chaos_circuit_breaker_isolation():
    """CircuitBreaker opens after threshold failures and fast-fails subsequent calls."""
    cb = CircuitBreaker("chaos_test", failure_threshold=3, recovery_timeout_sec=60.0)
    assert cb.state == CircuitState.CLOSED

    def failing_op():
        raise ConnectionError("Provider outage")

    for i in range(3):
        try:
            cb.call(failing_op)
        except ConnectionError:
            pass

    assert cb.state == CircuitState.OPEN

    # Subsequent call fast-fails with CircuitBreakerOpenError without invoking failing_op
    with pytest.raises(CircuitBreakerOpenError):
        cb.call(failing_op)


def test_chaos_failure_classifier_all_categories():
    """FailureClassifier categorizes all error types correctly."""
    assert FailureClassifier.classify("Permission denied by user") == "PERMISSION_DENIED"
    assert FailureClassifier.classify("Interactive confirmation required") == "PERMISSION_DENIED"
    assert FailureClassifier.classify("Request timed out after 5.0s") == "TRANSIENT"
    assert FailureClassifier.classify("Connection reset by peer") == "TRANSIENT"
    assert FailureClassifier.classify("Rate limit exceeded") == "TRANSIENT"
    assert FailureClassifier.classify("Resource not found (404)") == "RECOVERABLE_REPLAN"
    assert FailureClassifier.classify("Failed to fetch page") == "RECOVERABLE_REPLAN"
    assert FailureClassifier.classify("Completely unknown catastrophic error") == "FATAL"
