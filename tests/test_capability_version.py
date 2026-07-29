from jarvisx.capabilities.capability_version import CapabilityVersion

def test_capability_version_compatibility():
    assert CapabilityVersion.is_compatible("1.1.0", "1.0.0") is True
    assert CapabilityVersion.is_compatible("1.0.0", "1.1.0") is False
    assert CapabilityVersion.is_compatible("2.0.0", "2.0.0") is True
