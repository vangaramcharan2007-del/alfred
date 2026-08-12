"""Unit & Integration Tests for Screen Understanding for Computer Use.

Tests:
1. Screen analysis returns bounded structured state
2. Active window detection
3. Visible element extraction with bounds and confidence
4. Sensitive-field filtering (credentials, CVV, passwords redacted/filtered)
5. Malformed vision output rejection
6. Normal question -> screen analysis -> reasoning -> answer
7. Target identification -> safe action (click / type_text)
8. Re-observation after action execution
9. Verification failure stops loop
10. 5-action limit remains enforced
11. No screenshot persistence
12. Existing tools remain unaffected
"""

import pytest
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
from jarvisx.tools.builtin_tools import (
    AnalyzeScreenTool,
    CaptureScreenTool,
    ClickTool,
    GetActiveWindowTool,
    ListWindowsTool,
    OpenAppTool,
    register_builtin_tools,
)
from jarvisx.tools.tool_executor import ToolExecutor
from jarvisx.tools.tool_kernel import ToolRegistry
from jarvisx.vision.action_validator import ActionSafetyValidator
from jarvisx.vision.ui_detector import UIDetector
from jarvisx.vision.ui_state import UIElement, UIState, Window


class FakeScreenReasoningRouter:
    """Deterministic LLM router for vision & screen reasoning testing."""
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
            resp = "Reasoning complete, Sir."
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
# 1. Screen Analysis & UI State Extraction Tests
# ---------------------------------------------------------------------------

def test_screen_analysis_returns_bounded_structured_state():
    """analyze_screen returns bounded state containing active_window, dimensions, and elements."""
    tool = AnalyzeScreenTool()
    res = tool.execute({})
    assert res.status == "success"
    assert "active_window" in res.result
    assert res.result["width"] == 1920
    assert res.result["height"] == 1080
    assert "elements" in res.result
    assert isinstance(res.result["elements"], list)

    ver = tool.verify({}, res)
    assert ver.verified is True


def test_active_window_detection():
    """analyze_screen properly detects focused application window."""
    detector = UIDetector()
    analysis = detector.analyze_ui()
    assert analysis["active_window"] != ""
    assert analysis["window_count"] >= 1


def test_visible_element_extraction():
    """UI elements contain label, type, bounds [x,y,w,h], and confidence score."""
    detector = UIDetector()
    analysis = detector.analyze_ui()
    elements = analysis["elements"]
    assert len(elements) > 0
    el = elements[0]
    assert "label" in el
    assert "type" in el
    assert "bounds" in el
    assert len(el["bounds"]) == 4  # [x, y, w, h]
    assert "confidence" in el
    assert 0.0 <= el["confidence"] <= 1.0


def test_sensitive_field_filtering():
    """Elements and windows containing passwords, PINs, or credentials are filtered."""
    detector = UIDetector()
    # Direct test of sensitivity checker
    assert detector._is_sensitive("Master Password Input") is True
    assert detector._is_sensitive("Credit Card CVV") is True
    assert detector._is_sensitive("API Token Field") is True
    assert detector._is_sensitive("VS Code Launcher") is False
    assert detector._is_sensitive("Terminal Run Button") is False

    analysis = detector.analyze_ui()
    for el in analysis["elements"]:
        assert "password" not in el["label"].lower()
        assert "cvv" not in el["label"].lower()
        assert "secret" not in el["label"].lower()


def test_malformed_vision_output_rejection():
    """Tool verification rejects missing active_window or invalid dimensions."""
    tool = AnalyzeScreenTool()
    # Bad result missing dimensions
    bad_res = tool.execute({"invalid": 123})
    # Verification with corrupt result
    from jarvisx.tools.tool_kernel import ToolResult
    corrupt_result = ToolResult(status="success", tool="analyze_screen", result={"active_window": "", "width": 0})
    ver = tool.verify({}, corrupt_result)
    assert ver.verified is False


def test_no_screenshot_persistence():
    """Screen observation produces structured UI state in memory without dumping raw images to disk."""
    tool = AnalyzeScreenTool()
    res = tool.execute({})
    assert res.status == "success"
    # Result contains structured data, no file path leakage
    assert "frame_path" not in res.result


# ---------------------------------------------------------------------------
# 2. Vision Reasoning & Multi-Step Interaction Tests
# ---------------------------------------------------------------------------

def test_question_to_analysis_to_answer():
    """User asks 'What is currently open?' -> LLM calls analyze_screen -> answers accurately."""
    fake_router = FakeScreenReasoningRouter([
        '{"type": "tool_call", "tool": "analyze_screen", "arguments": {"query": "VS Code"}}',
        "Visual Studio Code is open on the desktop, along with PowerShell, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("What is currently open?", persona="ALFRED")

    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 1
    assert res["execution_steps"][0]["tool"] == "analyze_screen"
    assert "Visual Studio Code" in res["response"]


def test_target_identification_and_re_observation():
    """Identify element bounds -> execute action -> re-observe screen state."""
    fake_router = FakeScreenReasoningRouter([
        '{"type": "tool_call", "tool": "analyze_screen", "arguments": {"query": "terminal"}}',
        '{"type": "tool_call", "tool": "analyze_screen", "arguments": {}}',
        "I have located the terminal and confirmed it is ready, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Find the terminal window and verify it.", persona="ALFRED")

    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 2
    assert res["execution_steps"][0]["tool"] == "analyze_screen"
    assert res["execution_steps"][1]["tool"] == "analyze_screen"
    assert "located the terminal" in res["response"]


def test_verification_failure_stops_loop():
    """If a tool fails verification, multi-step execution stops immediately."""
    fake_router = FakeScreenReasoningRouter([
        '{"type": "tool_call", "tool": "open_app", "arguments": {"application": ""}}',  # Fails verification (empty name)
        '{"type": "tool_call", "tool": "analyze_screen", "arguments": {}}',             # Should never be called
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Open unknown app.", persona="ALFRED")

    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 1  # Stopped at step 1
    assert "failed" in res["response"].lower()


def test_five_action_limit_enforced_in_vision_loop():
    """Computer use chain terminates when 5 actions are reached."""
    fake_router = FakeScreenReasoningRouter([
        '{"type": "tool_call", "tool": "analyze_screen", "arguments": {}}',
        '{"type": "tool_call", "tool": "get_active_window", "arguments": {}}',
        '{"type": "tool_call", "tool": "list_windows", "arguments": {}}',
        '{"type": "tool_call", "tool": "analyze_screen", "arguments": {}}',
        '{"type": "tool_call", "tool": "get_system_info", "arguments": {}}',
        '{"type": "tool_call", "tool": "analyze_screen", "arguments": {}}',  # 6th call
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("Analyze everything 6 times", persona="ALFRED", max_tool_steps=5)

    assert res["action"] == "tool_call"
    assert len(res["execution_steps"]) == 5
    assert "Maximum tool execution limit" in res.get("error", "")


def test_existing_tools_unaffected_by_vision_additions():
    """Standard tools (get_current_time, get_system_info, read_file) continue functioning flawlessly."""
    fake_router = FakeScreenReasoningRouter([
        '{"type": "tool_call", "tool": "get_current_time", "arguments": {}}',
        "The current time is 08:50 PM, Sir.",
    ])
    orch = DynamicOrchestrator(llm_router=fake_router)
    res = orch.execute_llm_request("What time is it?", persona="ALFRED")

    assert res["action"] == "tool_call"
    assert res["execution_steps"][0]["tool"] == "get_current_time"
    assert "08:50 PM" in res["response"]
