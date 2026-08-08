"""Unit and Chaos Tests for Phase 98: Reliability Kernel & Production Hardening."""

import pytest
import time
from pathlib import Path
from jarvisx.reliability.models import (
    EvolutionEvent,
    HealthState,
    RecoveryAction,
    RecoveryState,
)
from jarvisx.reliability.reliability_memory import ReliabilityMemory
from jarvisx.reliability.health_monitor import HealthMonitor
from jarvisx.reliability.backup_manager import BackupManager
from jarvisx.reliability.crash_recovery import CrashRecoveryEngine
from jarvisx.reliability.runtime_integrity import RuntimeIntegrityValidator
from jarvisx.reliability.reliability_engine import ReliabilityEngine


def test_reliability_memory_persistence_and_schema_version():
    db_file = "var/test_rel/test_mem.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = ReliabilityMemory(db_file)
    event = EvolutionEvent(
        id="evo_1",
        timestamp=time.time(),
        component="Planner",
        old_behavior="Static task ordering",
        new_behavior="Dependency weighted planner",
        reason="Reduced mission failures",
        validation_result="97% tests passed",
        impact_delta="+2 HSPW"
    )
    mem.record_evolution(event)

    new_mem = ReliabilityMemory(db_file)
    evos = new_mem.list_evolutions()
    assert len(evos) == 1
    assert evos[0].component == "Planner"
    assert evos[0].impact_delta == "+2 HSPW"


def test_health_monitor_adaptive_probing():
    db_file = "var/test_rel/test_health.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = ReliabilityMemory(db_file)
    monitor = HealthMonitor(mem)

    # Adaptive intervals
    assert monitor.get_adaptive_interval(is_active_mission=False, has_recent_failure=False) == 60
    assert monitor.get_adaptive_interval(is_active_mission=True, has_recent_failure=False) == 10
    assert monitor.get_adaptive_interval(has_recent_failure=True) == 1

    state = monitor.probe_health()
    assert state.memory_rss_mb > 0.0
    assert state.active_threads >= 1
    assert state.latency_ms >= 0.0


def test_backup_manager_snapshot_and_sha256_verification():
    db_file = "var/test_rel/test_backup_mem.db"
    backup_root = "var/test_rel/backups"

    mem = ReliabilityMemory(db_file)
    mgr = BackupManager(mem, backup_root=backup_root)

    # Create snapshot
    snap = mgr.create_snapshot()
    assert snap.status == "VERIFIED"
    assert snap.size_bytes >= 0

    # Verify SHA256 cryptographic integrity
    is_valid = mgr.verify_snapshot(snap.id)
    assert is_valid is True

    # Restore snapshot
    res = mgr.restore_snapshot(snap.id)
    assert res["status"] == "SUCCESS"


def test_crash_recovery_state_machine_and_throttling():
    db_file = "var/test_rel/test_crash.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = ReliabilityMemory(db_file)
    recovery = CrashRecoveryEngine(mem, max_restarts=3, cooldown_sec=60)

    # 1. First crash -> Soft Reset
    r1 = recovery.handle_exception("CodingAgent", ValueError("Mock syntax error"))
    assert r1["status"] == "RECOVERED"
    assert r1["action"] == RecoveryAction.SOFT_RESTART.value

    # 2. Second crash -> Soft Reset
    r2 = recovery.handle_exception("CodingAgent", KeyError("Mock key error"))
    assert r2["status"] == "RECOVERED"

    # 3. Third crash -> Soft Reset
    r3 = recovery.handle_exception("CodingAgent", TimeoutError("Mock timeout"))
    assert r3["status"] == "RECOVERED"

    # 4. Fourth crash within cooldown window -> Restart Loop Prevention -> Safe Mode!
    r4 = recovery.handle_exception("CodingAgent", RuntimeError("Mock loop crash"))
    assert r4["status"] == "SAFE_MODE"
    assert r4["action"] == RecoveryAction.SAFE_MODE.value
    assert recovery.state == RecoveryState.SAFE_MODE


def test_runtime_integrity_and_safe_repair():
    db_file = "var/test_rel/test_integ.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = ReliabilityMemory(db_file)
    validator = RuntimeIntegrityValidator(mem)

    # Level 1 verify
    report = validator.verify_integrity()
    assert "all_healthy" in report

    # Level 2 safe repair
    repair = validator.safe_repair("reliability.db")
    assert repair["status"] == "REPAIRED"
    assert repair["level"] == 2


def test_reliability_engine_doctor_and_evolution():
    engine = ReliabilityEngine()
    doc = engine.doctor()
    assert "health" in doc
    assert "snapshots_count" in doc

    evos = engine.evolution_list()
    assert len(evos) >= 1
    assert any(e["component"] == "CodingAgent" for e in evos)
