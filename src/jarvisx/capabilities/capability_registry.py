from __future__ import annotations
from typing import Dict, List, Optional
from jarvisx.capabilities.capability_adapter import CapabilityAdapter
from jarvisx.capabilities.capability_manifest import CapabilityManifest
from jarvisx.capabilities.capability_version import CapabilityVersion
from jarvisx.core.logging import StructuredLogger

class CapabilityRegistry:
    def __init__(self):
        self.adapters: Dict[str, CapabilityAdapter] = {}
        self.logger = StructuredLogger()

    def register(self, adapter: CapabilityAdapter) -> None:
        self.validate_manifest(adapter.manifest)
        self.adapters[adapter.manifest.name] = adapter
        self.logger.write("info", f"Registered capability {adapter.manifest.name}", event="capability_registry")

    def remove(self, name: str) -> None:
        if name in self.adapters:
            del self.adapters[name]
            self.logger.write("info", f"Removed capability {name}", event="capability_registry")

    def discover(self, category: Optional[str] = None) -> List[CapabilityAdapter]:
        if category:
            return [adapter for adapter in self.adapters.values() if adapter.manifest.category == category]
        return list(self.adapters.values())

    def query(self, name: str) -> Optional[CapabilityAdapter]:
        return self.adapters.get(name)

    def validate_manifest(self, manifest: CapabilityManifest) -> bool:
        if not manifest.name or not manifest.version:
            raise ValueError("Manifest must have name and version")
        return True

    def check_compatibility(self, name: str, required_version: str) -> bool:
        adapter = self.query(name)
        if not adapter:
            return False
        return CapabilityVersion.is_compatible(adapter.manifest.version, required_version)
