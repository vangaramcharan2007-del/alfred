import pytest
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.meta.capability_introspection import CapabilityIntrospector

@pytest.mark.asyncio
async def test_capability_introspection_and_gap_detection():
    registry = CapabilityRegistry()
    await registry.register(CapabilityDescriptor(
        id="architecture.agent",
        name="Architecture Agent",
        version="1.0.0",
        author="Jarvis X",
        category="design",
        supported_actions=["design"],
        handler=lambda **kw: None
    ))

    introspector = CapabilityIntrospector(registry=registry)
    intro = introspector.introspect()

    assert intro["total_capabilities"] >= 1
    assert "design" in intro["categories"]

    analysis = introspector.analyze_mission("Build mobile iOS application with end to end testing")
    assert "mobile.testing" in analysis["missing_capabilities"]
    assert len(analysis["recommendations"]) >= 1
