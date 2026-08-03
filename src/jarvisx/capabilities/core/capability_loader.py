from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry

class CapabilityLoader:
    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        self.registry = registry or CapabilityRegistry()

    async def load_from_manifest(self, manifest_path: str) -> CapabilityDescriptor:
        path = Path(manifest_path)
        if not path.exists():
            raise FileNotFoundError(f"Manifest file not found at {manifest_path}")

        data = json.loads(path.read_text(encoding="utf-8"))
        descriptor = CapabilityDescriptor(
            id=data["id"],
            name=data["name"],
            version=data.get("version", "1.0.0"),
            author=data.get("author", "Jarvis X"),
            category=data.get("category", "general"),
            permissions=data.get("permissions", []),
            dependencies=data.get("dependencies", []),
            supported_actions=data.get("supported_actions", [])
        )

        await self.registry.register(descriptor)
        return descriptor
