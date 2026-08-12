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
    assert len(names) == 6


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
