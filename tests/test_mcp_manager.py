import pytest
from jarvisx.mcp.mcp_server_registry import MCPServerRegistry, MCPServerConfig
from jarvisx.mcp.mcp_manager import MCPManager
from jarvisx.mcp.mcp_capability_bridge import MCPCapabilityBridge
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry

@pytest.mark.asyncio
async def test_mcp_manager_and_bridge():
    server_registry = MCPServerRegistry()
    server_registry.register_server(MCPServerConfig(name="filesystem_test", server_type="Filesystem"))

    mcp_manager = MCPManager(server_registry=server_registry)
    client = await mcp_manager.connect_server("filesystem_test")
    assert client.is_connected is True
    assert "filesystem_test" in mcp_manager.list_connected_servers()

    cap_registry = CapabilityRegistry()
    bridge = MCPCapabilityBridge(mcp_manager=mcp_manager, capability_registry=cap_registry)

    descriptor = await bridge.bridge_server("filesystem_test")
    assert descriptor.id == "mcp.filesystem_test"
    assert "filesystem_action" in descriptor.supported_actions

    res = await cap_registry.execute("mcp.filesystem_test", "filesystem_action", file_path="main.py")
    assert res["status"] == "success"
