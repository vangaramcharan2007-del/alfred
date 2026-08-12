"""Unit Tests for Tool & Action Execution Kernel.

Covers: tool registry, permission gateway, tool executor pipeline,
built-in tools, security boundaries, and argument validation.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

from jarvisx.tools.tool_kernel import (
    PermissionLevel,
    Tool,
    ToolRegistry,
    ToolResult,
    ToolSpec,
)
from jarvisx.tools.builtin_tools import (
    CreateFileTool,
    GetCurrentTimeTool,
    GetSystemInfoTool,
    ListDirectoryTool,
    OpenAppTool,
    ReadFileTool,
    register_builtin_tools,
)
from jarvisx.tools.permission_gateway import PermissionGateway
from jarvisx.tools.tool_executor import ToolExecutor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_registry():
    """Ensure fresh registry for every test."""
    ToolRegistry.reset_instance()
    yield
    ToolRegistry.reset_instance()


@pytest.fixture
def registry():
    reg = ToolRegistry()
    register_builtin_tools(reg)
    return reg


@pytest.fixture
def executor(registry):
    return ToolExecutor(registry=registry, gateway=PermissionGateway())


# ---------------------------------------------------------------------------
# 1. ToolRegistry
# ---------------------------------------------------------------------------

def test_registry_list_tools(registry):
    tools = registry.list_tools()
    names = {t.name for t in tools}
    assert "get_current_time" in names
    assert "get_system_info" in names
    assert "list_directory" in names
    assert "read_file" in names
    assert "create_file" in names
    assert "open_app" in names
    assert "capture_screen" in names
    assert len(names) >= 6


def test_registry_get_known_tool(registry):
    tool = registry.get("get_current_time")
    assert tool is not None
    assert tool.spec().name == "get_current_time"


def test_registry_get_unknown_tool(registry):
    assert registry.get("secret_tool") is None
    assert registry.get("rm_rf_slash") is None


def test_registry_validate_valid_args(registry):
    result = registry.validate("list_directory", {"path": "/tmp"})
    assert result["valid"] is True


def test_registry_validate_missing_required(registry):
    result = registry.validate("list_directory", {})
    assert result["valid"] is False
    assert "Missing required" in result["error"]


def test_registry_validate_unknown_arg(registry):
    result = registry.validate("get_current_time", {"bogus": "value"})
    assert result["valid"] is False
    assert "Unknown argument" in result["error"]


def test_registry_validate_wrong_type(registry):
    result = registry.validate("list_directory", {"path": 12345})
    assert result["valid"] is False
    assert "must be string" in result["error"]


def test_registry_validate_unknown_tool(registry):
    result = registry.validate("nonexistent_tool", {"x": 1})
    assert result["valid"] is False
    assert "Unknown tool" in result["error"]


# ---------------------------------------------------------------------------
# 2. Security Tests
# ---------------------------------------------------------------------------

def test_unknown_tool_rejected(executor):
    result = executor.execute("secret_tool", {})
    assert result.status == "failed"
    assert "Unknown tool" in result.error


def test_malformed_arguments_rejected(executor):
    result = executor.execute("list_directory", {})
    assert result.status == "failed"
    assert "Missing required" in result.error


def test_path_traversal_read(executor):
    """read_file on a non-existent traversal path returns structured failure."""
    result = executor.execute("read_file", {"path": "../../etc/passwd"})
    assert result.status == "failed"


def test_restricted_tool_blocked():
    """A tool with RESTRICTED permission must be blocked."""

    class RestrictedTool(Tool):
        def spec(self):
            return ToolSpec(
                name="delete_system",
                description="Deletes system files.",
                input_schema={"type": "object", "properties": {}, "required": []},
                permission_level=PermissionLevel.RESTRICTED,
            )

        def execute(self, arguments):
            return ToolResult(status="success", tool="delete_system", result="deleted")

    reg = ToolRegistry()
    reg.register(RestrictedTool())
    ex = ToolExecutor(registry=reg, gateway=PermissionGateway())
    result = ex.execute("delete_system", {})
    assert result.status == "failed"
    assert "RESTRICTED" in result.error or "blocked" in result.error.lower()


def test_confirm_denied_non_interactive(executor):
    """CONFIRM tools must be denied in non-interactive mode."""
    result = executor.execute("create_file", {"path": "test.txt", "content": "hello"}, interactive=False)
    assert result.status == "failed"
    assert "non-interactive" in result.error.lower() or "denied" in result.error.lower()


def test_tool_exception_returns_structured_failure():
    """Tool that throws exception returns structured failure."""

    class CrashingTool(Tool):
        def spec(self):
            return ToolSpec(
                name="crasher",
                description="Always crashes.",
                input_schema={"type": "object", "properties": {}, "required": []},
                permission_level=PermissionLevel.SAFE,
            )

        def execute(self, arguments):
            raise RuntimeError("Intentional crash for testing")

    reg = ToolRegistry()
    reg.register(CrashingTool())
    ex = ToolExecutor(registry=reg, gateway=PermissionGateway())
    result = ex.execute("crasher", {})
    assert result.status == "failed"
    assert "Intentional crash" in result.error


def test_create_file_blocks_system_paths(executor):
    """create_file must refuse system-critical locations."""
    result = executor.execute("create_file", {"path": "C:\\Windows\\evil.txt", "content": "hacked"}, interactive=False)
    assert result.status == "failed"


def test_no_secrets_in_tool_results(executor):
    """System info must not leak OPENROUTER_API_KEY or similar secrets."""
    result = executor.execute("get_system_info", {})
    result_str = str(result.to_dict())
    assert "OPENROUTER_API_KEY" not in result_str
    assert "sk-or-" not in result_str
    env_key = os.environ.get("OPENROUTER_API_KEY", "")
    if env_key:
        assert env_key not in result_str


def test_tool_output_cannot_execute_code():
    """Tool results are data, not executable — verify ToolResult is a plain dataclass."""
    result = ToolResult(status="success", tool="test", result="__import__('os').system('echo hacked')")
    assert isinstance(result.to_dict(), dict)
    assert result.to_dict()["result"] == "__import__('os').system('echo hacked')"
    # The result is just a string, never eval'd


# ---------------------------------------------------------------------------
# 3. Built-in Tool Functional Tests
# ---------------------------------------------------------------------------

def test_get_current_time(executor):
    result = executor.execute("get_current_time", {})
    assert result.status == "success"
    assert result.verified is True
    assert "time" in result.result
    assert "date" in result.result


def test_get_system_info(executor):
    result = executor.execute("get_system_info", {})
    assert result.status == "success"
    assert result.verified is True
    assert "os" in result.result
    assert "architecture" in result.result


def test_list_directory_valid(executor):
    result = executor.execute("list_directory", {"path": "."})
    assert result.status == "success"
    assert result.verified is True
    assert result.result["count"] > 0


def test_list_directory_missing(executor):
    result = executor.execute("list_directory", {"path": "/nonexistent_path_abc123"})
    assert result.status == "failed"
    assert "does not exist" in result.error


def test_read_file_valid(executor):
    result = executor.execute("read_file", {"path": "pyproject.toml"})
    assert result.status == "success"
    assert result.verified is True
    assert "jarvisx" in result.result["content"].lower() or len(result.result["content"]) > 0


def test_read_file_missing(executor):
    result = executor.execute("read_file", {"path": "nonexistent_file_xyz.txt"})
    assert result.status == "failed"
    assert "does not exist" in result.error


def test_create_file_with_verification():
    """Test create_file in a temp directory (bypasses CONFIRM via direct tool.execute)."""
    tool = CreateFileTool()
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "hello.py")
        result = tool.execute({"path": target, "content": "print('hello')"})
        assert result.status == "success"
        verified = tool.verify({"path": target, "content": "print('hello')"}, result)
        assert verified.verified is True
        assert Path(target).read_text() == "print('hello')"


# ---------------------------------------------------------------------------
# 4. Permission Gateway
# ---------------------------------------------------------------------------

def test_permission_safe_auto_approved():
    gw = PermissionGateway()
    spec = ToolSpec(name="test", description="", input_schema={}, permission_level=PermissionLevel.SAFE)
    result = gw.check(spec, {})
    assert result["allowed"] is True


def test_permission_restricted_blocked():
    gw = PermissionGateway()
    spec = ToolSpec(name="test", description="", input_schema={}, permission_level=PermissionLevel.RESTRICTED)
    result = gw.check(spec, {})
    assert result["allowed"] is False


def test_permission_confirm_denied_non_interactive():
    gw = PermissionGateway()
    spec = ToolSpec(name="test", description="", input_schema={}, permission_level=PermissionLevel.CONFIRM)
    result = gw.check(spec, {}, interactive=False)
    assert result["allowed"] is False


# ---------------------------------------------------------------------------
# 5. ToolExecutor.parse_tool_call
# ---------------------------------------------------------------------------

def test_parse_tool_call_valid():
    text = '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}'
    result = ToolExecutor.parse_tool_call(text)
    assert result is not None
    assert result["tool"] == "get_current_time"


def test_parse_tool_call_normal_response():
    result = ToolExecutor.parse_tool_call("The CPU uses scheduling algorithms to manage processes.")
    assert result is None


def test_parse_tool_call_malformed_json():
    result = ToolExecutor.parse_tool_call('{"type": "tool_call", "tool": }')
    assert result is None


def test_parse_tool_call_missing_type():
    result = ToolExecutor.parse_tool_call('{"tool": "get_current_time", "arguments": {}}')
    assert result is None


def test_parse_tool_call_missing_tool():
    result = ToolExecutor.parse_tool_call('{"type": "tool_call", "arguments": {}}')
    assert result is None


def test_parse_tool_call_missing_arguments():
    result = ToolExecutor.parse_tool_call('{"type": "tool_call", "tool": "get_current_time"}')
    assert result is None


def test_parse_tool_call_embedded_json():
    text = 'Some preamble text {"type": "tool_call", "tool": "list_directory", "arguments": {"path": "."}} trailing'
    result = ToolExecutor.parse_tool_call(text)
    assert result is not None
    assert result["tool"] == "list_directory"


# ---------------------------------------------------------------------------
# 6. End-to-end ToolExecutor pipeline
# ---------------------------------------------------------------------------

def test_executor_end_to_end_safe_tool(executor):
    result = executor.execute("get_current_time", {})
    d = result.to_dict()
    assert d["status"] == "success"
    assert d["tool"] == "get_current_time"
    assert d["verified"] is True
    assert d["result"]["time"]


def test_executor_system_prompt_generation(executor):
    prompt = executor.build_tool_system_prompt()
    assert "get_current_time" in prompt
    assert "get_system_info" in prompt
    assert "tool_call" in prompt


def test_parse_tool_call_markdown_code_block():
    text = '```json\n{\n  "type": "tool_call",\n  "tool": "get_system_info",\n  "arguments": {}\n}\n```'
    result = ToolExecutor.parse_tool_call(text)
    assert result is not None
    assert result["tool"] == "get_system_info"


# ---------------------------------------------------------------------------
# 7. DynamicOrchestrator End-to-End Integration Tests
# ---------------------------------------------------------------------------

class FakeLLMRouter:
    def __init__(self, responses: list | dict):
        self.responses = responses
        self.call_history = []
        self._index = 0

    def route_request_sync(self, prompt: str, require_offline: bool = False, model_override: str = None):
        self.call_history.append(prompt)
        if isinstance(self.responses, list):
            if self._index < len(self.responses):
                resp = self.responses[self._index]
                self._index += 1
            else:
                resp = "Default fake response"
            return {
                "status": "success",
                "provider_id": "fake.local",
                "result": {"status": "AVAILABLE", "response": resp}
            }
        elif isinstance(self.responses, dict):
            for key, resp in self.responses.items():
                if key in prompt:
                    return {
                        "status": "success",
                        "provider_id": "fake.local",
                        "result": {"status": "AVAILABLE", "response": resp}
                    }
            return {
                "status": "success",
                "provider_id": "fake.local",
                "result": {"status": "AVAILABLE", "response": "Default fake response"}
            }


def test_orchestrator_safe_tool_get_current_time():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
        "The current time is 12:00 PM, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("What time is it?", persona="ALFRED")
    assert res["action"] == "tool_call"
    assert res["tool"] == "get_current_time"
    assert res["tool_result"]["status"] == "success"
    assert res["tool_result"]["verified"] is True
    assert "response" in res


def test_orchestrator_safe_tool_get_system_info():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "get_system_info", "arguments": {}}',
        "You have 16 GB of RAM available, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("How much RAM do I have?", persona="ALFRED")
    assert res["action"] == "tool_call"
    assert res["tool"] == "get_system_info"
    assert res["tool_result"]["status"] == "success"
    assert res["tool_result"]["verified"] is True
    assert "response" in res


def test_orchestrator_create_file_confirmation_deny():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "create_file", "arguments": {"path": "test_deny.py", "content": "print(1)"}}',
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    # interactive=False triggers non-interactive confirmation denial
    res = orch.execute_llm_request("Create hello.py", persona="ALFRED", interactive=False)
    assert res["action"] == "tool_call"
    assert res["tool"] == "create_file"
    assert res["tool_result"]["status"] == "failed"
    assert "non-interactive" in res["tool_result"]["error"].lower() or "denied" in res["tool_result"]["error"].lower()


def test_orchestrator_create_file_confirmation_approved(monkeypatch):
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    with tempfile.TemporaryDirectory() as tmp:
        target_path = os.path.join(tmp, "hello.py")
        fake_router = FakeLLMRouter([
            f'{{"type": "tool_call", "tool": "create_file", "arguments": {{"path": "{target_path.replace(chr(92), "/")}", "content": "print(\\"Hello\\")"}}}}',
            "Created hello.py successfully, Sir.",
        ])
        orch = DynamicOrchestrator(llm_router=fake_router)
        # Mock sys.stdin.isatty and input()
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr("builtins.input", lambda prompt="": "y")

        res = orch.execute_llm_request("Create hello.py", persona="ALFRED", interactive=True)
        assert res["action"] == "tool_call"
        assert res["tool"] == "create_file"
        assert res["tool_result"]["status"] == "success"
        assert res["tool_result"]["verified"] is True
        assert Path(target_path).exists()
        assert Path(target_path).read_text(encoding="utf-8") == 'print("Hello")'


def test_orchestrator_unknown_tool_rejection():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "secret_tool", "arguments": {}}',
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Use secret_tool", persona="ALFRED")
    assert res["action"] == "tool_call"
    assert res["tool"] == "secret_tool"
    assert res["tool_result"]["status"] == "failed"
    assert "Unknown tool" in res["tool_result"]["error"]


def test_orchestrator_conversational_response_no_tool():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        "CPU scheduling selects which process will execute next.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Explain CPU scheduling in one sentence.", persona="ALFRED")
    assert res["action"] == "llm"
    assert "CPU scheduling selects" in res["response"]


# ---------------------------------------------------------------------------
# 8. Bounded Multi-Step Tool Execution Tests
# ---------------------------------------------------------------------------

def test_multi_step_single_tool_still_works():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
        "The time is 12:00 PM, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("What time is it?", persona="ALFRED")
    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 1
    assert res["execution_steps"][0]["tool"] == "get_current_time"
    assert res["response"] == "The time is 12:00 PM, Sir."


def test_multi_step_two_dependent_tools():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "list_directory", "arguments": {"path": "."}}',
        '{"type": "tool_call", "tool": "read_file", "arguments": {"path": "pyproject.toml"}}',
        "I have listed the directory and read pyproject.toml, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("List files and read pyproject.toml", persona="ALFRED")
    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 2
    assert res["execution_steps"][0]["tool"] == "list_directory"
    assert res["execution_steps"][1]["tool"] == "read_file"
    assert res["response"] == "I have listed the directory and read pyproject.toml, Sir."


def test_multi_step_three_tools():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
        '{"type": "tool_call", "tool": "get_system_info", "arguments": {}}',
        '{"type": "tool_call", "tool": "list_directory", "arguments": {"path": "."}}',
        "Completed all 3 diagnostic steps, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Run full system diagnostic", persona="ALFRED")
    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 3
    assert res["execution_steps"][0]["tool"] == "get_current_time"
    assert res["execution_steps"][1]["tool"] == "get_system_info"
    assert res["execution_steps"][2]["tool"] == "list_directory"
    assert res["response"] == "Completed all 3 diagnostic steps, Sir."


def test_multi_step_fourth_call_rejected():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
        '{"type": "tool_call", "tool": "get_system_info", "arguments": {}}',
        '{"type": "tool_call", "tool": "list_directory", "arguments": {"path": "."}}',
        '{"type": "tool_call", "tool": "read_file", "arguments": {"path": "pyproject.toml"}}',
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Run 4 actions", persona="ALFRED", max_tool_steps=3)
    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 3
    assert "Maximum tool execution limit" in res.get("error", "") or "maximum action limit" in res.get("response", "").lower()


def test_multi_step_second_call_receives_first_result():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
        "Done.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    orch.execute_llm_request("Check time", persona="ALFRED")
    assert len(fake_router.call_history) == 2
    # Second call prompt must contain Step 1 tool result
    second_prompt = fake_router.call_history[1]
    assert "Execution history so far:" in second_prompt
    assert "get_current_time" in second_prompt


def test_multi_step_tool_failure_stops_chain():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "read_file", "arguments": {"path": "nonexistent_file_abc.txt"}}',
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Read missing file then get time", persona="ALFRED")
    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 1
    assert res["execution_steps"][0]["tool"] == "read_file"
    assert res["execution_steps"][0]["result"]["status"] == "failed"
    assert len(fake_router.call_history) == 1  # Stopped immediately after failure


def test_multi_step_permission_denial_stops_chain():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "create_file", "arguments": {"path": "test.txt", "content": "x"}}',
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Create file then get time", persona="ALFRED", interactive=False)
    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 1
    assert res["execution_steps"][0]["result"]["status"] == "failed"
    assert len(fake_router.call_history) == 1


def test_multi_step_verification_failure_stops_chain():
    from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
    from jarvisx.tools.tool_kernel import ToolRegistry, Tool, ToolSpec, ToolResult, PermissionLevel

    class UnverifiableTool(Tool):
        def spec(self):
            return ToolSpec(
                name="unverifiable_tool",
                description="Fails verification.",
                input_schema={"type": "object", "properties": {}, "required": []},
                permission_level=PermissionLevel.SAFE,
            )

        def execute(self, arguments):
            return ToolResult(status="success", tool="unverifiable_tool", result="ok")

        def verify(self, arguments, result):
            return ToolResult(status="success", tool="unverifiable_tool", result="ok", verified=False, error="Verification rejected")

    reg = ToolRegistry.get_instance()
    reg.register(UnverifiableTool())

    fake_router = FakeLLMRouter([
        '{"type": "tool_call", "tool": "unverifiable_tool", "arguments": {}}',
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Run unverifiable tool then get time", persona="ALFRED")
    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 1
    assert res["execution_steps"][0]["result"]["verified"] is False
    assert len(fake_router.call_history) == 1


