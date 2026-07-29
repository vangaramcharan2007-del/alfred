from __future__ import annotations
from typing import List, Dict
from jarvisx.capabilities.capability_registry import CapabilityRegistry
from jarvisx.capabilities.mcp.mcp_adapter import MCPAdapter
from jarvisx.capabilities.capability_manifest import CapabilityManifest
from jarvisx.capabilities.mcp.mcp_client import MCPClient

class MCPRegistry:
    def __init__(self, capability_registry: CapabilityRegistry):
        self.capability_registry = capability_registry
        self.mcp_adapters: Dict[str, MCPAdapter] = {}

    def register_mcp_server(self, manifest: CapabilityManifest, client: MCPClient) -> None:
        adapter = MCPAdapter(manifest, client)
        self.mcp_adapters[manifest.name] = adapter
        self.capability_registry.register(adapter)

    def remove_mcp_server(self, name: str) -> None:
        if name in self.mcp_adapters:
            self.capability_registry.remove(name)
            del self.mcp_adapters[name]
