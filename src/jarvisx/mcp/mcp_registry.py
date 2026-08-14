"""MCP Server Registry and Tool Adapter for Jarvis X: GENESIS.

Maintains registered MCP servers and mounts their tools into Jarvis X ToolRegistry.
"""

from __future__ import annotations
import asyncio
from typing import Dict, Any, List, Optional
from jarvisx.mcp.mcp_client import MCPClient, MCPToolDefinition
from jarvisx.tools.tool_kernel import Tool, ToolSpec, ToolResult, PermissionLevel, ToolRegistry


class AdaptedMCPTool(Tool):
    """Adapts an MCP Tool definition into a native Jarvis X Tool."""

    def __init__(self, client: MCPClient, definition: MCPToolDefinition, permission_level: PermissionLevel = PermissionLevel.CONFIRM):
        self.client = client
        self.definition = definition
        self.perm_level = permission_level

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=f"mcp_{self.client.server_id}_{self.definition.name}",
            description=f"[MCP:{self.client.server_id}] {self.definition.description}",
            input_schema=self.definition.input_schema,
            permission_level=self.perm_level,
            required_scope=f"mcp.{self.client.server_id}"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Run in executor or future
                res = asyncio.run_coroutine_threadsafe(self.client.call_tool(self.definition.name, arguments), loop).result(timeout=15.0)
            else:
                res = asyncio.run(self.client.call_tool(self.definition.name, arguments))
        except Exception:
            res = asyncio.run(self.client.call_tool(self.definition.name, arguments))

        status = res.get("status", "failed")
        return ToolResult(
            status=status,
            tool=self.spec().name,
            result=res.get("content"),
            error=res.get("error")
        )


class MCPRegistry:
    """Central registry for MCP servers and tools."""

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}

    def register_server(self, server_id: str, command: Optional[List[str]] = None, endpoint_url: Optional[str] = None) -> MCPClient:
        client = MCPClient(server_id=server_id, command=command, endpoint_url=endpoint_url)
        self.clients[server_id] = client
        return client

    def get_client(self, server_id: str) -> Optional[MCPClient]:
        return self.clients.get(server_id)

    async def mount_all_tools(self, target_registry: Optional[ToolRegistry] = None) -> int:
        """Mount all discovered MCP tools into the central Jarvis X ToolRegistry."""
        reg = target_registry or ToolRegistry.get_instance()
        mounted_count = 0

        for server_id, client in self.clients.items():
            if not client.is_connected:
                await client.connect()
            
            tools = await client.refresh_tools()
            for t in tools:
                # Default safety: Screen reading is SAFE, clicks/types are CONFIRM
                perm = PermissionLevel.SAFE if any(term in t.name.lower() for term in ("read", "inspect", "get", "list", "see", "screen")) else PermissionLevel.CONFIRM
                adapted = AdaptedMCPTool(client=client, definition=t, permission_level=perm)
                reg.register(adapted)
                mounted_count += 1

        return mounted_count


_GLOBAL_MCP_REGISTRY: Optional[MCPRegistry] = None


def get_mcp_registry() -> MCPRegistry:
    global _GLOBAL_MCP_REGISTRY
    if _GLOBAL_MCP_REGISTRY is None:
        _GLOBAL_MCP_REGISTRY = MCPRegistry()
    return _GLOBAL_MCP_REGISTRY
