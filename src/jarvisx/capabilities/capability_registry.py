from __future__ import annotations
from typing import Any, Dict, List, Optional
from jarvisx.capabilities.capability_adapter import CapabilityAdapter
from jarvisx.capabilities.capability_manifest import CapabilityContract, CapabilityManifest
from jarvisx.capabilities.capability_version import CapabilityVersion
from jarvisx.core.logging import StructuredLogger

class CapabilityRegistry:
    def __init__(self, *, logger: Optional[StructuredLogger] = None, health: Optional[Any] = None):
        self.adapters: Dict[str, CapabilityAdapter] = {}
        self.metadata: Dict[str, CapabilityContract] = {}
        self.aliases: Dict[str, str] = {}
        self.logger = logger or StructuredLogger()
        self.health = health

    def register(self, adapter: CapabilityAdapter) -> None:
        self.validate_manifest(adapter.manifest)
        capability_id = adapter.id
        self.adapters[capability_id] = adapter
        self.metadata[capability_id] = adapter.contract()
        self.aliases[adapter.manifest.name] = capability_id
        self.logger.write(
            "info",
            f"Registered capability {adapter.manifest.name}",
            event="capability_registry",
            capability_id=capability_id,
        )

    def remove(self, name: str) -> None:
        capability_id = self._normalize_id(name)
        if capability_id in self.adapters:
            adapter = self.adapters[capability_id]
            del self.adapters[capability_id]
            self.metadata.pop(capability_id, None)
            self.aliases.pop(adapter.manifest.name, None)
            self.logger.write("info", f"Removed capability {name}", event="capability_registry", capability_id=capability_id)

    def discover(self, category: Optional[str] = None) -> List[CapabilityAdapter]:
        if category:
            return [adapter for adapter in self.adapters.values() if adapter.manifest.category == category]
        return list(self.adapters.values())

    def query(self, name: str) -> Optional[CapabilityAdapter]:
        return self.adapters.get(self._normalize_id(name))

    def query_by_id(self, capability_id: str) -> Optional[CapabilityAdapter]:
        return self.query(capability_id)

    def get_metadata(self, capability_id: str) -> Optional[CapabilityContract]:
        adapter = self.query(capability_id)
        if not adapter:
            return None
        health_status = self._health_status(adapter.id)
        return adapter.contract(health_status=health_status)

    def list_metadata(self, category: Optional[str] = None) -> List[CapabilityContract]:
        return [
            metadata
            for metadata in (self.get_metadata(adapter.id) for adapter in self.discover(category))
            if metadata is not None
        ]

    def query_actions(self, capability_id: str) -> List[str]:
        adapter = self.query(capability_id)
        if not adapter:
            return []
        return adapter.available_actions

    def available_actions(self, capability_id: str) -> List[str]:
        return self.query_actions(capability_id)

    def report_unhealthy(self) -> List[CapabilityContract]:
        if not self.health:
            return []
        unhealthy = []
        for adapter in self.adapters.values():
            status = self.health.get_status(adapter.id)
            if not status.available or not status.healthy or status.last_error:
                unhealthy.append(adapter.contract(health_status=status.to_dict()))
        return unhealthy

    def validate_manifest(self, manifest: CapabilityManifest) -> bool:
        if not manifest.capability_id or not manifest.name or not manifest.version:
            raise ValueError("Manifest must have id/name and version")
        if not manifest.description:
            raise ValueError("Manifest must have description")
        if not isinstance(manifest.permissions, list):
            raise ValueError("Manifest permissions must be a list")
        if not isinstance(manifest.available_actions, list):
            raise ValueError("Manifest actions must be a list")
        return True

    def check_compatibility(self, name: str, required_version: str) -> bool:
        adapter = self.query(name)
        if not adapter:
            return False
        return CapabilityVersion.is_compatible(adapter.manifest.version, required_version)

    def set_health(self, health: Any) -> None:
        self.health = health

    def _normalize_id(self, name: str) -> str:
        return self.aliases.get(name, name)

    def _health_status(self, capability_id: str) -> Dict[str, Any]:
        if not self.health:
            return {}
        status = self.health.get_status(capability_id)
        return status.to_dict()
