from jarvisx.capabilities.capability_events import (
    CapabilityLoaded,
    CapabilityFailed,
    CapabilityUpdated,
    CapabilityDisabled
)

def test_capability_events():
    event1 = CapabilityLoaded("test_cap", "1.0.0")
    assert event1.capability_name == "test_cap"
    assert event1.version == "1.0.0"

    event2 = CapabilityFailed("test_cap", "Connection timeout")
    assert event2.error == "Connection timeout"

    event3 = CapabilityUpdated("test_cap", "1.1.0")
    assert event3.new_version == "1.1.0"

    event4 = CapabilityDisabled("test_cap", "User disabled")
    assert event4.reason == "User disabled"
