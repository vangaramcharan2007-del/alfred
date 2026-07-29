import pytest
from jarvisx.capabilities.capability_adapter import CapabilityAdapter
from jarvisx.capabilities.capability_manifest import CapabilityManifest

class DummyAdapter(CapabilityAdapter):
    async def initialize(self): pass
    async def execute(self, inputs): return {"result": "ok"}
    async def health_check(self): return True
    async def shutdown(self): pass

@pytest.mark.asyncio
async def test_adapter_interface():
    manifest = CapabilityManifest(name="test", version="1.0.0", api_version="v1", description="Test", category="test")
    adapter = DummyAdapter(manifest)
    
    await adapter.initialize()
    result = await adapter.execute({})
    assert result == {"result": "ok"}
    
    health = await adapter.health_check()
    assert health is True
    
    await adapter.shutdown()
