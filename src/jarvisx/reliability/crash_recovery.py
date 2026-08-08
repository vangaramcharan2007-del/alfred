"""Crash Recovery Engine for Phase 98 Reliability Kernel."""

from __future__ import annotations
import time
import traceback
import uuid
from typing import Dict, List, Optional
from jarvisx.reliability.models import CrashEvent, RecoveryAction, RecoveryState
from jarvisx.reliability.reliability_memory import ReliabilityMemory


class CrashRecoveryEngine:
    """State-machine crash recovery with restart throttling (max 3 restarts in 60s) to prevent restart loops."""

    def __init__(self, memory: Optional[ReliabilityMemory] = None, max_restarts: int = 3, cooldown_sec: int = 60):
        self.memory = memory or ReliabilityMemory()
        self.max_restarts = max_restarts
        self.cooldown_sec = cooldown_sec
        self.state = RecoveryState.RUNNING
        self.recent_restart_timestamps: List[float] = []

    def handle_exception(self, component: str, exc: Exception) -> Dict[str, Any]:
        """Intercept unhandled exception, determine recovery action, and transition state."""
        self.state = RecoveryState.FAILURE_DETECTED
        now = time.time()

        # Prune restart timestamps older than cooldown window
        self.recent_restart_timestamps = [t for t in self.recent_restart_timestamps if now - t < self.cooldown_sec]

        # Check restart throttling
        if len(self.recent_restart_timestamps) >= self.max_restarts:
            action = RecoveryAction.SAFE_MODE
            self.state = RecoveryState.SAFE_MODE
            print(f"  [Crash Recovery]: Restart loop detected ({len(self.recent_restart_timestamps)} restarts in {self.cooldown_sec}s). Engaging SAFE_MODE.")
        else:
            action = RecoveryAction.SOFT_RESTART
            self.recent_restart_timestamps.append(now)
            self.state = RecoveryState.SOFT_RESET
            print(f"  [Crash Recovery]: Soft reset initiated for {component} (Attempt {len(self.recent_restart_timestamps)}/{self.max_restarts}).")

        crash = CrashEvent(
            id=f"crash_{int(now*1000)}",
            timestamp=now,
            component=component,
            exception_type=type(exc).__name__,
            stack_trace=traceback.format_exc(),
            recovery_action=action
        )
        self.memory.record_crash(crash)

        return {
            "status": "RECOVERED" if action != RecoveryAction.SAFE_MODE else "SAFE_MODE",
            "action": action.value,
            "crash_id": crash.id,
            "restarts_in_window": len(self.recent_restart_timestamps)
        }
