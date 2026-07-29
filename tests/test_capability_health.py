import pytest
from jarvisx.capabilities.capability_health import CapabilityHealth

def test_capability_health_tracking():
    health = CapabilityHealth()
    health.register("test_cap")
    
    health.record_call("test_cap", success=True, latency_ms=100.0)
    health.record_call("test_cap", success=False, latency_ms=200.0)
    
    status = health.get_status("test_cap")
    assert status.total_calls == 2
    assert status.successful_calls == 1
    assert status.failures == 1
    assert status.reliability_score == 0.5
    assert status.latency_ms == 150.0
