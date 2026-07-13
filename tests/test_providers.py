import pytest
import asyncio
from jarvisx.core.providers.provider_registry import BaseProvider, ProviderCapability, ProviderRegistry
from jarvisx.core.providers.fallback_manager import FallbackManager

class MockProvider(BaseProvider):
    def __init__(self, name: str, priority: int, healthy: bool = True):
        self._name = name
        self._priority = priority
        self.healthy = healthy
        
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("TEST_CAT", self._name, self._priority, False)
        
    async def check_health(self) -> bool:
        return self.healthy
        
    async def benchmark(self) -> float:
        return 10.0 if self.healthy else float('inf')


@pytest.mark.asyncio
async def test_provider_registration_order():
    registry = ProviderRegistry()
    registry.register(MockProvider("p2", 20))
    registry.register(MockProvider("p1", 10))
    registry.register(MockProvider("p3", 30))
    
    providers = registry.get_providers("TEST_CAT")
    assert len(providers) == 3
    # Should be sorted by priority
    assert providers[0].capability.name == "p1"
    assert providers[1].capability.name == "p2"
    assert providers[2].capability.name == "p3"

@pytest.mark.asyncio
async def test_fallback_manager_initialization():
    registry = ProviderRegistry()
    p1 = MockProvider("p1", 10, healthy=False)
    p2 = MockProvider("p2", 20, healthy=True)
    registry.register(p1)
    registry.register(p2)
    
    fallback = FallbackManager(registry)
    await fallback.initialize()
    
    active = fallback.get_active("TEST_CAT")
    assert active is not None
    assert active.capability.name == "p2"

@pytest.mark.asyncio
async def test_fallback_manager_runtime_failure():
    registry = ProviderRegistry()
    p1 = MockProvider("p1", 10, healthy=True)
    p2 = MockProvider("p2", 20, healthy=True)
    registry.register(p1)
    registry.register(p2)
    
    fallback = FallbackManager(registry)
    await fallback.initialize()
    
    active = fallback.get_active("TEST_CAT")
    assert active.capability.name == "p1"
    
    # Simulate p1 failing during runtime
    p1.healthy = False
    new_active = await fallback.handle_failure("TEST_CAT", "p1")
    
    assert new_active is not None
    assert new_active.capability.name == "p2"
    assert fallback.get_active("TEST_CAT").capability.name == "p2"
