from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.mcp.mcp_manager import MCPManager
from jarvisx.mcp.mcp_client import MCPClient
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor

class MCPCapabilityBridge:
    def __init__(
        self,
        mcp_manager: Optional[MCPManager] = None,
        capability_registry: Optional[CapabilityRegistry] = None
    ):
        self.mcp_manager = mcp_manager or MCPManager()
        self.capability_registry = capability_registry or CapabilityRegistry()

    async def bridge_server(self, server_name: str) -> CapabilityDescriptor:
        client = self.mcp_manager.get_client(server_name)
        if not client:
            client = await self.mcp_manager.connect_server(server_name)

        tools = await client.list_tools()
        action_names = [t["name"] for t in tools]

        async def _mcp_handler(action: str, **kwargs):
            return await client.call_tool(action, kwargs)

        descriptor = CapabilityDescriptor(
            id=f"mcp.{server_name}",
            name=f"MCP {client.server_type} ({server_name})",
            version="1.0.0",
            author="MCP Integration",
            category="mcp",
            permissions=["EXECUTE", "READ", "WRITE"],
            supported_actions=action_names,
            handler=_mcp_handler
        )

        await self.capability_registry.register(descriptor)
        return descriptor
