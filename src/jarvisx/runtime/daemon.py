"""Sovereign Always-On Daemon for Jarvis X (Phase 104)."""

from __future__ import annotations
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from jarvisx.events.event_bus import EventBus
from jarvisx.events.models import EventType, SystemEvent
from jarvisx.events.proactive_scheduler import ProactiveScheduler
from jarvisx.runtime.heartbeat import DaemonHeartbeatMonitor
from jarvisx.runtime.ipc_server import IPCServer
from jarvisx.runtime.lifecycle import DaemonLifecycleManager
from jarvisx.runtime.pid_lock import PIDLockManager
from jarvisx.runtime.presence_state_machine import PresenceState, PresenceStateMachine
from jarvisx.runtime.resource_governor import ResourceGovernor
from jarvisx.runtime.service_manager import WindowsServiceManager
from jarvisx.runtime.state import DaemonRuntimeState, RuntimeStateManager

logger = logging.getLogger("jarvisx.daemon")


class JarvisDaemon:
    """Master Always-On Background Daemon orchestrating PID locking, IPC server, event bus, proactive scheduler, presence states, and health heartbeat."""

    def __init__(
        self,
        var_dir: Optional[str] = None,
        ipc_port: int = 10404,
        command_handler: Optional[Callable[[str], Dict[str, Any]]] = None,
    ):
        self.var_dir = Path(var_dir or "var")
        self.var_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.var_dir / "logs" / "daemon.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.pid_manager = PIDLockManager(str(self.var_dir / "runtime" / "jarvisd.pid"))
        self.state_manager = RuntimeStateManager(str(self.var_dir / "runtime" / "state.json"))
        self.lifecycle_manager = DaemonLifecycleManager(self.pid_manager, self.state_manager)

        self.presence = PresenceStateMachine(PresenceState.OFFLINE)
        self.governor = ResourceGovernor()

        self.event_bus = EventBus()
        self.scheduler = ProactiveScheduler(self.event_bus)
        self.service_manager = WindowsServiceManager(str(self.var_dir / "scripts"))

        self.command_handler = command_handler
        self.ipc_server = IPCServer(
            port=ipc_port,
            command_handler=self._handle_ipc_command,
            event_handler=self._handle_ipc_event,
            briefing_handler=self._handle_ipc_briefing,
            status_handler=self._handle_ipc_status,
            shutdown_handler=self.stop,
        )
        self.heartbeat = DaemonHeartbeatMonitor(self.state_manager, interval_seconds=30.0)

        # Register shutdown hooks
        self.lifecycle_manager.register_shutdown_hook(self.ipc_server.stop)
        self.lifecycle_manager.register_shutdown_hook(self.scheduler.stop)
        self.lifecycle_manager.register_shutdown_hook(self.event_bus.stop)
        self.lifecycle_manager.register_shutdown_hook(self.heartbeat.stop)

    def log(self, message: str):
        """Append log message to daemon logfile."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [jarvisd] {message}\n"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception:
            pass

    def is_running(self) -> bool:
        """Check if daemon process is active."""
        return self.pid_manager.get_running_pid() is not None

    def start(self, block: bool = False) -> Dict[str, Any]:
        """Acquire PID lock, boot subsystem threads, and transition state to RUNNING."""
        ok, reason = self.pid_manager.acquire()
        if not ok:
            return {"status": "ALREADY_RUNNING", "error": reason}

        self.presence.transition_to(PresenceState.BOOTING, reason="Acquired PID lock")
        pid = os.getpid()
        self.log(f"Starting Jarvis X Daemon (PID: {pid})...")

        # 1. Update State
        self.state_manager.update_state(
            status="RUNNING",
            pid=pid,
            started_at=time.time(),
            active_services=[
                "PIDLockManager",
                "PresenceStateMachine",
                "ResourceGovernor",
                "IPCServer",
                "EventBus",
                "ProactiveScheduler",
                "HeartbeatMonitor",
            ],
            health="GREEN",
        )

        # 2. Install Signal Traps
        self.lifecycle_manager.install_signal_handlers()

        # 3. Start Subsystem Workers
        self.event_bus.start()
        self.scheduler.start()
        self.ipc_server.start()
        self.heartbeat.start()

        # 4. Trigger SYSTEM_BOOT event
        boot_event = SystemEvent(
            event_type=EventType.SYSTEM_BOOT,
            priority=10,
            origin="JarvisDaemon",
            payload={"pid": pid, "start_time": time.time()},
        )
        self.event_bus.publish(boot_event)

        self.presence.transition_to(PresenceState.READY, reason="All subsystems initialized")
        self.log("All daemon subsystems successfully initialized and running.")

        res = {
            "status": "STARTED",
            "pid": pid,
            "port": self.ipc_server.port,
            "presence": self.presence.current_state.value,
            "log_file": str(self.log_file),
            "state_file": str(self.state_manager.state_file),
        }

        if block:
            try:
                while self.is_running():
                    time.sleep(1.0)
            except KeyboardInterrupt:
                self.stop()

        return res

    def stop(self) -> Dict[str, Any]:
        """Initiate graceful shutdown of all workers and release lock."""
        self.log("Stopping Jarvis X Daemon...")
        if self.presence.can_transition_to(PresenceState.STOPPING):
            self.presence.transition_to(PresenceState.STOPPING, reason="Shutdown requested")
        self.lifecycle_manager.shutdown()
        if self.presence.can_transition_to(PresenceState.OFFLINE):
            self.presence.transition_to(PresenceState.OFFLINE, reason="Shutdown completed")
        return {"status": "STOPPED"}

    def get_status(self) -> DaemonRuntimeState:
        """Retrieve current daemon state."""
        return self.state_manager.load_state()

    def generate_startup_script(self) -> Dict[str, Any]:
        """Generate Windows startup registration scripts."""
        return self.service_manager.generate_startup_artifacts()

    # --- Internal IPC Dispatch Handlers ---
    def _handle_ipc_command(self, cmd: str) -> Dict[str, Any]:
        if self.command_handler:
            try:
                res = self.command_handler(cmd)
                current_state = self.state_manager.load_state()
                self.state_manager.update_state(total_commands_executed=current_state.total_commands_executed + 1)
                return res
            except Exception as e:
                return {"status": "ERROR", "error": str(e)}
        return {"status": "SUCCESS", "echo": cmd}

    def _handle_ipc_event(self, event_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            event_type = EventType(event_name)
        except Exception:
            event_type = EventType.CUSTOM

        evt = SystemEvent(event_type=event_type, payload=payload, origin="IPCClient")
        evt_id = self.event_bus.publish(evt)
        current_state = self.state_manager.load_state()
        self.state_manager.update_state(
            total_events_processed=current_state.total_events_processed + 1,
            last_event=event_name,
        )
        return {"status": "PUBLISHED", "event_id": evt_id}

    def _handle_ipc_briefing(self) -> str:
        return self.scheduler.synthesize_morning_briefing()

    def _handle_ipc_status(self) -> Dict[str, Any]:
        state = self.get_status()
        return {
            "status": state.status,
            "pid": state.pid,
            "uptime_seconds": state.uptime_seconds,
            "active_services": state.active_services,
            "memory_rss_mb": state.memory_rss_mb,
            "cpu_percent": state.cpu_percent,
            "health": state.health,
            "total_commands_executed": state.total_commands_executed,
            "total_events_processed": state.total_events_processed,
            "last_event": state.last_event,
        }
