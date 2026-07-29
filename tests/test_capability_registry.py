import pytest
from jarvisx.capabilities.capability_manifest import CapabilityManifest
from jarvisx.capabilities.capability_registry import CapabilityRegistry
from jarvisx.capabilities.capability_adapter import CapabilityAdapter

class MockAdapter(CapabilityAdapter):
    async def initialize(self): pass
    async def execute(self, inputs): return {}
    async def health_check(self): return True
    async def shutdown(self): pass

def test_registry_register_and_discover():
    registry = CapabilityRegistry()
    manifest = CapabilityManifest(name="test", version="1.0.0", api_version="v1", description="Test", category="test")
    adapter = MockAdapter(manifest)
    
    registry.register(adapter)
    assert registry.query("test") == adapter
    
    discovered = registry.discover("test")
    assert len(discovered) == 1
    assert discovered[0] == adapter

def test_registry_remove():
    registry = CapabilityRegistry()
    manifest = CapabilityManifest(name="test", version="1.0.0", api_version="v1", description="Test", category="test")
    adapter = MockAdapter(manifest)
    
    registry.register(adapter)
    registry.remove("test")
    assert registry.query("test") is None
