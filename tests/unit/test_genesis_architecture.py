"""Unit tests for Jarvis X: GENESIS Architectural Upgrade.

Covers:
- MCP Client & Registry
- UACC Computer Use Adapter & Engine
- Llama.cpp Provider Interface
- Computer-Use Structured Observability & Credential Redaction
- Decoupled Dodo Payments Monetization Gateway
- ToolRegistry with UACC Computer Control Tool
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from jarvisx.mcp.mcp_client import MCPClient, MCPToolDefinition
from jarvisx.mcp.mcp_registry import MCPRegistry, AdaptedMCPTool
from jarvisx.computer_use.uacc_adapter import UACCAdapter
from jarvisx.computer_use.computer_use_engine import ComputerUseEngine
from jarvisx.llm.llamacpp_provider import LlamaCppProvider
from jarvisx.observability.computer_use_logger import ComputerUseLogger, redact_sensitive
from jarvisx.monetization.dodo_gateway import DodoPaymentsGateway
from jarvisx.tools.tool_kernel import ToolRegistry, PermissionLevel
from jarvisx.tools.builtin_tools import UACCComputerControlTool, register_builtin_tools


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
