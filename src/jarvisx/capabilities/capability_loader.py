from __future__ import annotations
import json
from pathlib import Path
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

    def load_built_in_sync(self) -> None:
        manifests_dir = Path(__file__).resolve().parent / "manifests"
        self.load_local_sync(manifests_dir)

    async def load_built_in(self) -> None:
        self.load_built_in_sync()

    def load_local_sync(self, path: str | Path) -> None:
        directory = Path(path)
        if not directory.exists():
            return
        if not directory.is_dir():
            raise ValueError(f"Capability manifest path is not a directory: {directory}")
        
        for manifest_path in sorted(directory.glob("*.json")):
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                adapter = self._adapter_from_manifest_data(data)
                self.registry.register(adapter)
            except Exception as exc:
                self.registry.logger.write(
                    "warning",
                    "capability_loader.manifest_failed",
                    path=str(manifest_path),
                    error=str(exc),
                )

    async def load_local(self, path: str | Path) -> None:
        self.load_local_sync(path)

    async def load_external(self, url: str) -> None:
        pass

    def _adapter_from_manifest_data(self, data: dict) -> CapabilityAdapter:
        valid_keys = {
            "name",
            "version",
            "api_version",
            "description",
            "category",
            "id",
            "inputs",
            "outputs",
            "requirements",
            "permissions",
            "actions",
            "tools",
            "confidence",
        }
        filtered_data = {key: value for key, value in data.items() if key in valid_keys}
        manifest = CapabilityManifest(**filtered_data)
        return DummyAdapter(manifest)
