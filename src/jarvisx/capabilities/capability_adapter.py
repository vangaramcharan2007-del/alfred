from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict

from jarvisx.capabilities.capability_manifest import CapabilityManifest

class CapabilityAdapter(ABC):
    def __init__(self, manifest: CapabilityManifest):
        self.manifest = manifest

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
