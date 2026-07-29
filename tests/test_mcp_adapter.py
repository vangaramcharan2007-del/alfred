import pytest
from jarvisx.capabilities.mcp.mcp_adapter import MCPAdapter
from jarvisx.capabilities.mcp.mcp_client import MCPClient
from jarvisx.capabilities.capability_manifest import CapabilityManifest

class MockClient(MCPClient):
    async def connect(self):
        self.connected = True
    async def call_tool(self, name, args):
        return {"called": name, "args": args}
    async def close(self):
        self.connected = False

@pytest.mark.asyncio
async def test_mcp_adapter():
    manifest = CapabilityManifest(name="mcp_test", version="1.0.0", api_version="v1", description="Test", category="test")
    client = MockClient()
    adapter = MCPAdapter(manifest, client)
    
    assert await adapter.health_check() is False
    
    await adapter.initialize()
    assert await adapter.health_check() is True
    
    result = await adapter.execute({"arg1": "val1"})
    assert result == {"called": "mcp_test", "args": {"arg1": "val1"}}
    
    await adapter.shutdown()
    assert await adapter.health_check() is False
