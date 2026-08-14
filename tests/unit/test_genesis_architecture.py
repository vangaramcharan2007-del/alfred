"""Unit tests for Jarvis X: GENESIS Architectural Upgrade.

Covers:
- Architectural Independence between Inference, Computer Use, and Monetization
- MCP Client & Registry Lifecycle
- UACC Computer Use Adapter & Dual Backend Execution
- Llama.cpp Provider Interface
- Safety Gate & Permission Enforcer Integration
- Computer-Use Structured Observability & Credential Redaction
- Decoupled Dodo Payments Monetization Gateway
"""

import sys
import inspect
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from jarvisx.mcp.mcp_client import MCPClient, MCPToolDefinition
from jarvisx.mcp.mcp_registry import MCPRegistry, AdaptedMCPTool
from jarvisx.computer_use.uacc_adapter import UACCAdapter
from jarvisx.computer_use.computer_use_engine import ComputerUseEngine
from jarvisx.llm.llamacpp_provider import LlamaCppProvider
from jarvisx.llm.llm_provider import LLMProvider
from jarvisx.observability.computer_use_logger import ComputerUseLogger, redact_sensitive
from jarvisx.monetization.dodo_gateway import DodoPaymentsGateway
from jarvisx.tools.tool_kernel import ToolRegistry, PermissionLevel, ToolResult
from jarvisx.tools.builtin_tools import UACCComputerControlTool, register_builtin_tools
from jarvisx.tools.permission_gateway import PermissionGateway


def test_redact_sensitive_credentials():
    raw_text = "My API key is AIzaSyD1234567890abcdef1234567890 and password: secret_pass"
    cleaned = redact_sensitive(raw_text)
    assert "AIzaSy" not in cleaned
    assert "[REDACTED_SECRET]" in cleaned


def test_uacc_adapter_screen_inspection():
    uacc = UACCAdapter()
    res = uacc.inspect_screen()
    assert res["status"] == "success"
    assert "screen" in res
    assert "width" in res["screen"]
    assert "height" in res["screen"]
    assert "active_window" in res["screen"]


def test_uacc_adapter_execute_action():
    uacc = UACCAdapter()
    res = uacc.execute_action("inspect", {})
    assert res["status"] == "success"

    # Unknown action should return failed status
    res_bad = uacc.execute_action("invalid_action_xyz", {})
    assert res_bad["status"] == "failed"


def test_computer_use_engine_vscode_creation(tmp_path):
    engine = ComputerUseEngine()
    test_file = tmp_path / "test_script.py"
    code = "import numpy as np\nprint('Matrix Multiplication')\n"
    
    with patch("subprocess.Popen") as mock_popen:
        res = engine.type_code_in_vscode(str(test_file), code)
        assert res["status"] == "success"
        assert res["filename"] == "test_script.py"
        assert test_file.exists()


def test_mcp_client_tool_discovery():
    client = MCPClient(server_id="uacc_desktop")
    t_def = MCPToolDefinition(
        name="mouse_click",
        description="Click at coordinate",
        input_schema={"type": "object", "properties": {"x": {"type": "integer"}}},
        server_id="uacc_desktop"
    )
    client.discovered_tools["mouse_click"] = t_def

    adapted = AdaptedMCPTool(client, t_def, PermissionLevel.CONFIRM)
    spec = adapted.spec()
    assert spec.name == "mcp_uacc_desktop_mouse_click"
    assert spec.permission_level == PermissionLevel.CONFIRM


@pytest.mark.asyncio
async def test_llamacpp_provider_interface():
    provider = LlamaCppProvider(endpoint="http://localhost:8080")
    assert provider.name == "llamacpp.local"
    assert "gguf_quantization" in provider.capabilities()
    
    # Check fallback on offline endpoint
    health = await provider.health()
    assert health["provider"] == "llamacpp.local"


def test_dodo_monetization_isolation():
    gateway = DodoPaymentsGateway(api_key="test_key", webhook_secret="test_secret")
    checkout = gateway.create_checkout_session("test@example.com", plan_id="pro")
    assert checkout["status"] == "success"
    assert "checkout_url" in checkout
    assert checkout["amount_usd"] == 19.99


def test_uacc_computer_control_tool_execution():
    tool = UACCComputerControlTool()
    spec = tool.spec()
    assert spec.name == "uacc_computer_control"
    assert spec.permission_level == PermissionLevel.CONFIRM

    # Screen inspect action should succeed
    res = tool.execute({"action": "inspect", "params": {}})
    assert res.status == "success"
    assert res.tool == "uacc_computer_control"


def test_architectural_independence_inference_and_computer_use():
    """Verify that inference providers have zero hard imports of computer use or GUI drivers."""
    import jarvisx.llm.llm_provider as llm_p
    import jarvisx.llm.ollama_provider as ollama_p
    import jarvisx.llm.llamacpp_provider as llama_p

    for mod in (llm_p, ollama_p, llama_p):
        source = inspect.getsource(mod)
        assert "ComputerUseEngine" not in source
        assert "UACCAdapter" not in source
        assert "pyautogui" not in source


def test_permission_gateway_enforcement_on_computer_use():
    """Verify that PermissionGateway enforces CONFIRM approval on computer-use actions."""
    gateway = PermissionGateway()
    tool = UACCComputerControlTool()
    
    # Non-interactive mode must deny CONFIRM actions
    res = gateway.check(tool.spec(), {"action": "click", "params": {"x": 100, "y": 100}}, interactive=False)
    assert res["allowed"] is False
    assert "CONFIRM" in res["reason"]

    # SAFE tools are auto-approved
    from jarvisx.tools.builtin_tools import GetCurrentTimeTool
    time_tool = GetCurrentTimeTool()
    res_safe = gateway.check(time_tool.spec(), {}, interactive=False)
    assert res_safe["allowed"] is True


def test_art_synthesizer_vector_strokes():
    """Verify ArtSynthesizer produces valid parametric strokes for characters."""
    from jarvisx.computer_use.art_synthesizer import ArtSynthesizer
    
    zoro_strokes = ArtSynthesizer.generate_zoro_strokes(960, 540)
    assert len(zoro_strokes) >= 15
    for s in zoro_strokes:
        assert "start" in s and len(s["start"]) == 2
        assert "end" in s and len(s["end"]) == 2

    ironman_strokes = ArtSynthesizer.generate_ironman_strokes(960, 540)
    assert len(ironman_strokes) >= 10
    for s in ironman_strokes:
        assert "start" in s and "end" in s


def test_uacc_mcp_server_tools_spec():
    """Verify standalone UACC MCP Server exposes all required computer-use tools."""
    from jarvisx.mcp.uacc_server import TOOLS_SPEC, handle_inspect_screen
    
    names = [t["name"] for t in TOOLS_SPEC]
    assert "uacc_inspect_screen" in names
    assert "uacc_launch_app" in names
    assert "uacc_mouse_click" in names
    assert "uacc_mouse_drag" in names
    assert "uacc_draw_stroke_sequence" in names

    screen_res = handle_inspect_screen()
    assert "width" in screen_res
    assert "height" in screen_res
    assert "active_window" in screen_res


def test_visual_agent_loop_milestone_planning():
    """Verify VisualAgentLoop decomposes complex visual goals into progressive stages (Level 2 & 5)."""
    from jarvisx.computer_use.visual_agent_loop import VisualAgentLoop
    
    agent_loop = VisualAgentLoop()
    session = agent_loop.plan_visual_milestones("Luffy vs Zoro duel", 960, 540)
    assert len(session.stages) == 3
    assert session.stages[0].name == "Primary Contours"
    assert session.stages[1].name == "Facial Features & Scars"
    assert session.stages[2].name == "Santoryu Blades & Haki Clash"
    assert sum(len(s.strokes) for s in session.stages) >= 50


@pytest.mark.asyncio
async def test_visual_agent_loop_conversational_refinement():
    """Verify VisualAgentLoop can apply conversational refinements to active artwork (Level 6)."""
    from jarvisx.computer_use.visual_agent_loop import VisualAgentLoop
    
    agent_loop = VisualAgentLoop()
    agent_loop.plan_visual_milestones("Zoro", 960, 540)
    
    with patch.object(agent_loop.client, "call_tool", return_value={"status": "success"}):
        with patch.object(agent_loop.client, "connect", return_value=True):
            agent_loop.client.is_connected = True
            refine_res = await agent_loop.apply_conversational_refinement("Add Conqueror's Haki lightning")
            assert refine_res["status"] == "success"
            assert refine_res["strokes_added"] > 0
            assert "Conqueror's Haki" in refine_res["refinement"]
