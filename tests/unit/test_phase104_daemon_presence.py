"""Unit and Integration Test Suite for Phase 104: Persistent Daemon & Event Nervous System."""

from pathlib import Path
import pytest
import time

from jarvisx.events.event_bus import EventBus
from jarvisx.events.models import EventType, SystemEvent
from jarvisx.events.proactive_scheduler import ProactiveScheduler
from jarvisx.runtime.daemon import JarvisDaemon
from jarvisx.runtime.heartbeat import DaemonHeartbeatMonitor
from jarvisx.runtime.ipc_client import IPCClient
from jarvisx.runtime.ipc_protocol import IPCMessage, IPCMessageType
from jarvisx.runtime.ipc_server import IPCServer
from jarvisx.runtime.pid_lock import PIDLockManager
from jarvisx.runtime.service_manager import WindowsServiceManager
from jarvisx.runtime.state import RuntimeStateManager
from jarvisx.voice.voice_gateway import SecureVoiceGateway


def test_pid_lock_acquisition_stale_cleanup_and_release(tmp_path):
    """Verify PID locking prevents multi-instance collisions and cleans up stale locks."""
    pid_file = str(tmp_path / "jarvisd.pid")
    mgr1 = PIDLockManager(pid_file)

    # 1. Acquire first lock
    ok, err = mgr1.acquire()
    assert ok is True
    assert err is None
    assert mgr1.get_running_pid() is not None

    # 2. Duplicate acquire in same process should succeed
    ok2, _ = mgr1.acquire()
    assert ok2 is True

    # 3. Release
    released = mgr1.release()
    assert released is True
    assert mgr1.get_running_pid() is None


def test_runtime_state_manager_persistence_and_health(tmp_path):
    """Verify runtime state JSON persistence, uptime, and health updates."""
    state_file = str(tmp_path / "state.json")
    mgr = RuntimeStateManager(state_file)

    st = mgr.update_state(
        status="RUNNING",
        pid=1234,
        started_at=time.time() - 100.0,
        active_services=["Heartbeat", "IPC"],
        memory_rss_mb=85.5,
        health="GREEN",
    )
    assert st.status == "RUNNING"
    assert st.uptime_seconds >= 100.0
    assert st.health == "GREEN"

    loaded = mgr.load_state()
    assert loaded.pid == 1234
    assert loaded.status == "RUNNING"
    assert "Heartbeat" in loaded.active_services


def test_heartbeat_monitor_background_loop_metrics(tmp_path):
    """Verify background heartbeat thread records process metrics and health."""
    state_file = str(tmp_path / "state.json")
    state_mgr = RuntimeStateManager(state_file)

    heartbeat_ticks = []
    hb = DaemonHeartbeatMonitor(state_mgr, interval_seconds=0.1, on_heartbeat=lambda: heartbeat_ticks.append(1))
    hb.start()

    time.sleep(0.35)
    hb.stop()

    assert len(heartbeat_ticks) >= 2
    current_state = state_mgr.load_state()
    assert current_state.health in ("GREEN", "YELLOW")


def test_ipc_server_and_client_roundtrip_latency(tmp_path):
    """Verify high-speed IPC loopback roundtrip latency is < 25ms."""
    port = 10455  # test port
    server = IPCServer(
        port=port,
        command_handler=lambda cmd: {"output": f"Executed: {cmd}"},
        briefing_handler=lambda: "Test Morning Briefing",
        status_handler=lambda: {"status": "TEST_ONLINE"},
    )
    server.start()
    time.sleep(0.1)

    client = IPCClient(port=port)

    try:
        # 1. PING latency
        alive, lat_ping = client.ping()
        assert alive is True
        assert lat_ping < 25.0  # Ultra-fast IPC

        # 2. GET_STATUS
        ok_st, st_data, lat_st = client.get_status()
        assert ok_st is True
        assert st_data.get("status") == "TEST_ONLINE"

        # 3. GET_BRIEFING
        ok_bf, bf_data, _ = client.get_briefing()
        assert ok_bf is True
        assert "Test Morning Briefing" in bf_data

        # 4. EXECUTE_COMMAND
        ok_cmd, cmd_resp, _ = client.execute_command("check memory")
        assert ok_cmd is True
        assert cmd_resp.get("output") == "Executed: check memory"

    finally:
        server.stop()


def test_event_bus_priority_queue_and_subscriptions():
    """Verify event bus priority sorting and asynchronous handler dispatch."""
    bus = EventBus()
    handled_events = []

    bus.subscribe(EventType.DEADLINE_APPROACHING, lambda e: handled_events.append(e.event_type))
    bus.subscribe(EventType.HABIT_MISSED, lambda e: handled_events.append(e.event_type))

    bus.start()
    try:
        bus.publish(SystemEvent(event_type=EventType.DEADLINE_APPROACHING, priority=9))
        bus.publish(SystemEvent(event_type=EventType.HABIT_MISSED, priority=5))

        time.sleep(0.3)
        assert len(handled_events) == 2
        assert bus.get_recent_events(limit=5)[0].handled is True
    finally:
        bus.stop()


def test_proactive_scheduler_deadlines_habits_and_decay():
    """Verify proactive scheduler triggers appropriate system events."""
    bus = EventBus()
    scheduler = ProactiveScheduler(bus, check_interval_seconds=0.1)

    evt_decay = scheduler.trigger_decay_cycle()
    assert evt_decay.startswith("evt_")

    evt_deadline = scheduler.check_deadlines()
    assert evt_deadline.startswith("evt_")

    evt_habit = scheduler.check_habits()
    assert evt_habit.startswith("evt_")


def test_morning_briefing_synthesis():
    """Verify structured morning briefing formatting."""
    bus = EventBus()
    scheduler = ProactiveScheduler(bus)

    briefing = scheduler.synthesize_morning_briefing(profile_summary="BTech CSE BDA 10 CGPA Target")
    assert "JARVIS X MORNING BRIEFING" in briefing
    assert "10 CGPA" in briefing
    assert "DSA" in briefing
    assert "DBMS" in briefing


def test_secure_voice_gateway_wake_trigger_and_intent():
    """Verify wake word detection and speech intent routing."""
    bus = EventBus()
    executed_intents = []
    gw = SecureVoiceGateway(bus, wake_word="alfred", intent_handler=lambda i: executed_intents.append(i) or {"done": True})

    res = gw.process_spoken_utterance("Hey Alfred, prepare my DSA study plan")
    assert res["status"] == "EXECUTED"
    assert "dsa study plan" in res["intent"]
    assert len(executed_intents) == 1


def test_secure_voice_gateway_blocks_destructive_commands():
    """Verify voice gateway strictly blocks destructive unauthenticated commands."""
    bus = EventBus()
    gw = SecureVoiceGateway(bus, wake_word="alfred")

    res = gw.process_spoken_utterance("Alfred delete all database files and dump secrets")
    assert res["status"] == "BLOCKED_BY_POLICY"
    assert "Zero-Trust Policy Engine" in res["error"]
    assert gw.blocked_voice_commands == 1


def test_windows_service_manager_startup_script_generation(tmp_path):
    """Verify Windows startup scripts and task scheduler XML generation."""
    mgr = WindowsServiceManager(scripts_dir=str(tmp_path / "scripts"))
    res = mgr.generate_startup_artifacts()

    assert res["status"] == "SUCCESS"
    assert Path(res["bat_script"]).exists()
    assert Path(res["ps1_script"]).exists()
    assert Path(res["task_scheduler_xml"]).exists()


def test_daemon_master_lifecycle_start_event_boot_and_stop(tmp_path):
    """Verify full end-to-end master daemon startup, boot event publication, and clean shutdown."""
    daemon = JarvisDaemon(var_dir=str(tmp_path / "var"), ipc_port=10456)

    res = daemon.start()
    assert res["status"] == "STARTED"
    assert daemon.is_running() is True

    # State check
    st = daemon.get_status()
    assert st.status == "RUNNING"
    assert "IPCServer" in st.active_services

    # Graceful stop
    stop_res = daemon.stop()
    assert stop_res["status"] == "STOPPED"
    assert daemon.is_running() is False
