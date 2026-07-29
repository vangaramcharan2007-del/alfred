import pytest
import os
import tempfile
import json
from jarvisx.capabilities.capability_loader import CapabilityLoader
from jarvisx.capabilities.capability_registry import CapabilityRegistry

@pytest.mark.asyncio
async def test_capability_loader_local():
    registry = CapabilityRegistry()
    loader = CapabilityLoader(registry)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manifest_path = os.path.join(temp_dir, "test.json")
        with open(manifest_path, "w") as f:
            json.dump({
                "name": "test_local",
                "version": "1.0.0",
                "api_version": "v1",
                "description": "Test local",
                "category": "test"
            }, f)
        
        await loader.load_local(temp_dir)
        
    adapter = registry.query("test_local")
    assert adapter is not None
    assert adapter.manifest.name == "test_local"
