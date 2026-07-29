from __future__ import annotations
from typing import Dict, Any
from jarvisx.capabilities.capability_adapter import CapabilityAdapter
from jarvisx.capabilities.capability_manifest import CapabilityManifest
from jarvisx.capabilities.mcp.mcp_client import MCPClient

class MCPAdapter(CapabilityAdapter):
    def __init__(self, manifest: CapabilityManifest, client: MCPClient):
        super().__init__(manifest)
        self.client = client
        self.initialized = False

    async def initialize(self) -> None:
        if not self.initialized:
            await self.client.connect()
            self.initialized = True

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if not self.initialized:
            await self.initialize()
        return await self.client.call_tool(self.manifest.name, inputs)

    async def health_check(self) -> bool:
        return self.initialized

    async def shutdown(self) -> None:
        if self.initialized:
            await self.client.close()
            self.initialized = False
