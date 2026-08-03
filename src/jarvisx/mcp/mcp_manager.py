from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.mcp.mcp_client import MCPClient
from jarvisx.mcp.mcp_server_registry import MCPServerRegistry, MCPServerConfig
from jarvisx.capabilities.coding.metrics import CodingMetrics

class MCPManager:
    def __init__(
        self,
        bus: Optional[HermesBus] = None,
        server_registry: Optional[MCPServerRegistry] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.bus = bus or HermesBus()
        self.server_registry = server_registry or MCPServerRegistry()
        self.metrics = metrics or CodingMetrics()
        self.clients: Dict[str, MCPClient] = {}

    async def connect_server(self, server_name: str) -> MCPClient:
        config = self.server_registry.get_server(server_name)
        if not config:
            await self.bus.publish(Event(
                type="mcp.server.failed",
                source="mcp_manager",
                payload={"server_name": server_name, "error": "Server config not found"}
            ))
            self.metrics.record_codebase_intelligence() # fallback
            raise KeyError(f"MCP server config for '{server_name}' not found.")

        client = MCPClient(server_name=config.name, server_type=config.server_type, config=config.params)
        try:
            connected = await client.connect()
            if connected:
                self.clients[server_name] = client
                self.metrics.provider_connections += 1

                await self.bus.publish(Event(
                    type="mcp.server.connected",
                    source="mcp_manager",
                    payload={"server_name": server_name, "server_type": config.server_type}
                ))
                return client
            else:
                raise RuntimeError("Connection returned False")
        except Exception as e:
            self.metrics.failed_connections += 1
            await self.bus.publish(Event(
                type="mcp.server.failed",
                source="mcp_manager",
                payload={"server_name": server_name, "error": str(e)}
            ))
            raise e

    async def disconnect_server(self, server_name: str) -> bool:
        if server_name in self.clients:
            await self.clients[server_name].disconnect()
            del self.clients[server_name]
            return True
        return False

    def get_client(self, server_name: str) -> Optional[MCPClient]:
        return self.clients.get(server_name)

    def list_connected_servers(self) -> List[str]:
        return [name for name, c in self.clients.items() if c.is_connected]
