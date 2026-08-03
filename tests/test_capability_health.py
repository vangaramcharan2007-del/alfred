import pytest
from jarvisx.capabilities.core.capability_health import CapabilityHealthMonitor, CapabilityHealthReport

def test_capability_health_monitor():
    monitor = CapabilityHealthMonitor()
    report = monitor.register_capability("cap.test", "1.1.0")

    assert report.status == "HEALTHY"
    assert report.version == "1.1.0"

    monitor.record_execution("cap.test", success=True, latency_ms=12.5)
    rep = monitor.get_report("cap.test")
    assert rep.execution_failures == 0
    assert rep.response_latency_ms == 12.5

    # Simulate 3 failures to trigger DEGRADED status
    monitor.record_execution("cap.test", success=False, latency_ms=50.0)
    monitor.record_execution("cap.test", success=False, latency_ms=50.0)
    monitor.record_execution("cap.test", success=False, latency_ms=50.0)

    rep_degraded = monitor.get_report("cap.test")
    assert rep_degraded.status == "DEGRADED"
    assert rep_degraded.execution_failures == 3
