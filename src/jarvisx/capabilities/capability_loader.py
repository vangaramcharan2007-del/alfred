from __future__ import annotations
from typing import List
import json
import os
from jarvisx.capabilities.capability_registry import CapabilityRegistry
from jarvisx.capabilities.capability_manifest import CapabilityManifest
from jarvisx.capabilities.capability_adapter import CapabilityAdapter

class DummyAdapter(CapabilityAdapter):
    async def initialize(self) -> None:
        pass
    async def execute(self, inputs: dict) -> dict:
        return {"status": "dummy_executed"}
    async def health_check(self) -> bool:
        return True
    async def shutdown(self) -> None:
        pass

class CapabilityLoader:
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    async def load_built_in(self) -> None:
        pass

    async def load_local(self, path: str) -> None:
        if not os.path.exists(path):
            return
        
        for file in os.listdir(path):
            if file.endswith(".json"):
                with open(os.path.join(path, file), "r") as f:
                    data = json.load(f)
                    # Filter data to match CapabilityManifest signature
                    valid_keys = {"name", "version", "api_version", "description", "category", "inputs", "outputs", "requirements", "permissions", "confidence"}
                    filtered_data = {k: v for k, v in data.items() if k in valid_keys}
                    manifest = CapabilityManifest(**filtered_data)
                    adapter = DummyAdapter(manifest)
                    self.registry.register(adapter)

    async def load_external(self, url: str) -> None:
        pass
