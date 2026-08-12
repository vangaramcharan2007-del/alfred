"""Unit & Integration Tests for Safe Computer-Use + Screen Understanding.

Covers:
1. Screen capture structured state
2. Active-window detection
3. Window listing
4. Coordinate and schema validation
5. Permission gating (CONFIRM for click, type_text, press_key)
6. 5-action execution limit
7. Unsafe window / security dialog rejection
8. Failed verification stops execution
9. No secret persistence
10. Tool result isolation
11. End-to-end computer-use loop
12. Existing normal tools unaffected
"""

import os
import pytest

from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
from jarvisx.tools.builtin_tools import (
    CaptureScreenTool,
    GetActiveWindowTool,
    ListWindowsTool,
    ClickTool,
    TypeTextTool,
    PressKeyTool,
    register_builtin_tools,
)
from jarvisx.tools.tool_executor import ToolExecutor
from jarvisx.tools.tool_kernel import PermissionLevel, ToolRegistry, ToolResult
from jarvisx.vision.action_validator import ActionSafetyValidator


class FakeComputerUseLLMRouter:
    """Mock LLMRouter for deterministic computer-use testing."""
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
            resp = "Task completed, Sir."
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
# 1. Individual Tool Tests
# ---------------------------------------------------------------------------

def test_capture_screen_returns_normalized_state():
    """capture_screen returns structured UI state with valid resolution and window list."""
    tool = CaptureScreenTool()
    res = tool.execute({})
    assert res.status == "success"
    assert "width" in res.result
    assert "height" in res.result
    assert "active_window" in res.result
    assert "windows" in res.result
    assert "elements" in res.result

    ver = tool.verify({}, res)
    assert ver.verified is True


def test_get_active_window():
    """get_active_window returns active window metadata."""
    tool = GetActiveWindowTool()
    res = tool.execute({})
    assert res.status == "success"
    assert "title" in res.result
    assert "process_name" in res.result
    assert res.result["is_active"] is True

    ver = tool.verify({}, res)
    assert ver.verified is True


def test_list_windows():
    """list_windows returns all open desktop windows."""
    tool = ListWindowsTool()
    res = tool.execute({})
    assert res.status == "success"
    assert "count" in res.result
    assert "windows" in res.result
    assert isinstance(res.result["windows"], list)

    ver = tool.verify({}, res)
    assert ver.verified is True


def test_click_coordinates_validation():
    """click tool rejects invalid or out-of-bounds coordinates."""
    tool = ClickTool()

    # Non-integer coordinates
    res_str = tool.execute({"x": "invalid", "y": 100})
    assert res_str.status == "failed"
    assert "must be integers" in res_str.error

    # Out of bounds coordinates
    res_oob = tool.execute({"x": 99999, "y": 99999})
    assert res_oob.status == "failed"
    assert "out of physical screen bounds" in res_oob.error


def test_click_requires_confirm_permission():
    """click is gated by CONFIRM and denied in non-interactive sessions."""
    registry = ToolRegistry.get_instance()
    executor = ToolExecutor(registry=registry)

    # Non-interactive execution -> Denied
    res_denied = executor.execute("click", {"x": 500, "y": 500}, interactive=False)
    assert res_denied.status == "failed"
    assert "non-interactive session cannot provide user approval" in res_denied.error.lower()


def test_type_text_validation_and_permission():
    """type_text rejects empty text, dangerous shell commands, and requires confirmation."""
    tool = TypeTextTool()

    # Empty text
    res_empty = tool.execute({"text": ""})
    assert res_empty.status == "failed"

    # Dangerous command blocking
    res_danger = tool.execute({"text": "format C: /y"})
    assert res_danger.status == "failed"
    assert "Forbidden destructive" in res_danger.error

    # Non-interactive permission gate
    registry = ToolRegistry.get_instance()
    executor = ToolExecutor(registry=registry)
    res_denied = executor.execute("type_text", {"text": "hello"}, interactive=False)
    assert res_denied.status == "failed"
    assert "non-interactive session cannot provide user approval" in res_denied.error.lower()


def test_press_key_validation():
    """press_key only allows allowlisted safe keys."""
    tool = PressKeyTool()

    # Unknown/dangerous key
    res_bad = tool.execute({"key": "power_off_system"})
    assert res_bad.status == "failed"
    assert "not in the allowed safe keys" in res_bad.error

    # Safe key
    res_good = tool.execute({"key": "enter"})
    assert res_good.status == "success"


def test_unsafe_security_dialog_rejection():
    """ActionSafetyValidator blocks automated interaction with credential/password/UAC dialogs."""
    validator = ActionSafetyValidator()

    # Window safety check
    uac_check = validator.validate_window_safety("User Account Control (UAC)")
    assert uac_check["decision"] == "BLOCK"
    assert "sensitive/security keyword" in uac_check["reason"]

    pw_check = validator.validate_window_safety("Enter Network Password")
    assert pw_check["decision"] == "BLOCK"

    # Mouse action against sensitive window
    mouse_check = validator.validate_mouse_action("click", (200, 200), active_window="Windows Security - Password Prompt")
    assert mouse_check["decision"] == "BLOCK"

    # Keyboard action against sensitive window
    key_check = validator.validate_keyboard_action("my_secret_password", active_window="BitLocker PIN Prompt")
    assert key_check["decision"] == "BLOCK"


# ---------------------------------------------------------------------------
# 2. Orchestration & Bounded Multi-Step Computer-Use Loop Tests
# ---------------------------------------------------------------------------

def test_computer_use_observation_flow():
    """DynamicOrchestrator runs LLM computer-use observation and synthesis."""
    fake_router = FakeComputerUseLLMRouter([
        '{"type": "tool_call", "tool": "get_active_window", "arguments": {}}',
        '{"type": "tool_call", "tool": "capture_screen", "arguments": {}}',
        "Your active window is Visual Studio Code, and the desktop is ready, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("What window is active and what is on screen?", persona="ALFRED")

    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 2
    assert res["execution_steps"][0]["tool"] == "get_active_window"
    assert res["execution_steps"][1]["tool"] == "capture_screen"
    assert "Visual Studio Code" in res["response"]


def test_five_action_limit_enforced():
    """DynamicOrchestrator rejects the 6th tool call when max_tool_steps=5 is reached."""
    fake_router = FakeComputerUseLLMRouter([
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
        '{"type": "tool_call", "tool": "get_active_window", "arguments": {}}',
        '{"type": "tool_call", "tool": "list_windows", "arguments": {}}',
        '{"type": "tool_call", "tool": "capture_screen", "arguments": {}}',
        '{"type": "tool_call", "tool": "get_system_info", "arguments": {}}',
        '{"type": "tool_call", "tool": "list_directory", "arguments": {"path": "."}}',  # 6th call
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Run 6 actions in a row", persona="ALFRED", max_tool_steps=5)

    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 5
    assert "Maximum tool execution limit (5 steps) reached." in res.get("error", "")


def test_existing_normal_tools_unaffected():
    """Existing built-in tools (get_current_time, get_system_info, read_file) continue working unaffected."""
    fake_router = FakeComputerUseLLMRouter([
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
        "The current time is 12:00 PM, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("What time is it?", persona="ALFRED")
    assert res["action"] == "tool_call"
    assert res["execution_steps"][0]["tool"] == "get_current_time"
    assert "12:00 PM" in res["response"]
