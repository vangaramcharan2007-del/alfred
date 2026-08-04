from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from jarvisx.capabilities.capability_manifest import CapabilityContract, CapabilityManifest

class CapabilityAdapter(ABC):
    def __init__(self, manifest: CapabilityManifest):
        self.manifest = manifest

    @property
    def id(self) -> str:
        return self.manifest.capability_id

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def version(self) -> str:
        return self.manifest.version

    @property
    def description(self) -> str:
        return self.manifest.description

    @property
    def permissions_required(self) -> list[str]:
        return list(self.manifest.permissions)

    @property
    def available_actions(self) -> list[str]:
        return self.manifest.available_actions

    @property
    def available_tools(self) -> list[str]:
        return self.manifest.available_tools

    @property
    def initialization_method(self) -> str:
        return "initialize"

    def contract(self, health_status: Optional[Dict[str, Any]] = None) -> CapabilityContract:
        return self.manifest.to_contract(
            health_status=health_status,
            initialization_method=self.initialization_method,
        )

    def metadata(self, health_status: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.contract(health_status=health_status).to_dict()

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass
