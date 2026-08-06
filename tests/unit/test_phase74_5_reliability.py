"""Unit and Integration Tests for Phase 74.5: Alfred Reliability Hardening.

Tests StartupManager lifecycle, HealthMonitor unified heartbeat schema, CapabilityRealityRegistry,
ServiceRecoverySupervisor crash recovery loops, RealVoicePipeline degraded modes, and StructuredCrashLogger.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.startup.startup_manager import StartupManager
from jarvisx.startup.health_monitor import HealthMonitor
from jarvisx.startup.recovery import ServiceRecoverySupervisor
from jarvisx.automation.capability_registry import CapabilityRealityRegistry
from jarvisx.observability.crash_logger import StructuredCrashLogger
from jarvisx.automation.real_voice_runtime import RealVoicePipeline


def test_startup_manager_lifecycle():
    """Verify StartupManager OS detection, registration, and config validation."""
    mgr = StartupManager()
    os_info = mgr.detect_os()
    assert "platform" in os_info
    assert "is_windows" in os_info

    reg_res = mgr.register_windows_startup()
    assert reg_res["status"] in ("REGISTERED", "BYPASS")
    assert "startup_script" in reg_res

    val_res = mgr.validate_startup_config()
    assert val_res["status"] == "VALIDATED"
    assert val_res["valid"] is True


def test_health_monitor_heartbeat_and_sqlite_storage():
    """Verify HealthMonitor unified heartbeat schema generation and SQLite storage."""
    hm = HealthMonitor()
    hb = hm.generate_heartbeat(daemon_status="healthy", tray_status="running", voice_status="ready", memory_status="connected")

    assert hb["daemon"] == "healthy"
    assert hb["tray"] == "running"
    assert hb["voice"] == "ready"
    assert hb["memory"] == "connected"
    assert "last_check" in hb

    # Verify SQLite memory storage
    memories = hm.memory.search_memory("heartbeat", top_k=5)
    assert len(memories) >= 1
    assert memories[0]["value"]["daemon"] == "healthy"

    # Test unhealthy component reporting
    unhealthy = hm.get_unhealthy_components({"daemon": "crashed", "tray": "stopped", "voice": "ready", "memory": "connected"})
    assert "daemon" in unhealthy
    assert "tray" in unhealthy
    assert "voice" not in unhealthy


def test_capability_reality_registry():
    """Verify CapabilityRealityRegistry execution types and UNKNOWN capability blocking."""
    reg = CapabilityRealityRegistry()
    
    # Test PHYSICAL capability
    v1 = reg.verify_capability("system cleaner")
    assert v1["verified"] is True
    assert v1["capability"]["execution_type"] == "PHYSICAL"

    # Test UNKNOWN capability blocking
    v2 = reg.verify_capability("teleport user to mars")
    assert v2["verified"] is False
    assert v2["status"] == "BLOCKED"
    assert "UNKNOWN" in v2["reason"]

    # Verify Kernel blocks UNKNOWN requests
    kernel = PersonalOSKernel()
    res = kernel.execute_objective("teleport user to mars")
    assert res["status"] == "BLOCKED"
    assert "UNKNOWN" in res["reason"]


def test_recovery_supervisor_crash_loops():
    """Verify ServiceRecoverySupervisor handles recovery and guards against infinite crash loops."""
    kernel = PersonalOSKernel()
    recovery = ServiceRecoverySupervisor(max_retries_per_window=2, window_seconds=60)

    # First recovery attempt
    r1 = recovery.attempt_recovery("daemon", os_kernel=kernel)
    assert r1["status"] == "RECOVERED"
    assert r1["retry_number"] == 1

    # Second recovery attempt
    r2 = recovery.attempt_recovery("daemon", os_kernel=kernel)
    assert r2["status"] == "RECOVERED"
    assert r2["retry_number"] == 2

    # Third attempt should be BLOCKED due to retry cap (preventing infinite loops)
    r3 = recovery.attempt_recovery("daemon", os_kernel=kernel)
    assert r3["status"] == "BLOCKED"
    assert "prevented" in r3["reason"]


def test_voice_runtime_degraded_statuses():
    """Verify RealVoicePipeline status validation (VOICE_READY, VOICE_DEGRADED, VOICE_OFFLINE)."""
    voice = RealVoicePipeline()
    assert voice.pipeline_status in ("VOICE_READY", "VOICE_DEGRADED", "VOICE_OFFLINE")

    start_res = voice.start_listening()
    assert start_res["status"] == "active"
    assert voice.pipeline_status in ("VOICE_READY", "VOICE_DEGRADED")

    pause_res = voice.pause_listening()
    assert pause_res["status"] == "paused"
    assert voice.pipeline_status == "VOICE_OFFLINE"


def test_structured_crash_logging():
    """Verify StructuredCrashLogger writes and reads JSON log entries in var/logs/."""
    logger = StructuredCrashLogger(log_dir="var/logs")
    entry = logger.log_crash("test_subsystem", "Simulated runtime memory error")
    assert entry["event_type"] == "CRASH"
    assert entry["status"] == "FAILED"
    assert entry["component"] == "test_subsystem"

    recent = logger.read_recent_logs(limit=5)
    assert len(recent) >= 1
    assert any(log.get("event_type") == "CRASH" for log in recent)
