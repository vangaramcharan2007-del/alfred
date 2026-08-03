import pytest
from jarvisx.mcp.mcp_manager import MCPManager

def test_integration_mcp_foundation_manager():
    mgr = MCPManager()
    servers = mgr.server_registry.list_servers()
    assert isinstance(servers, list)
