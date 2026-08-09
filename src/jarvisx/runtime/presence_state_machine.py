"""Presence State Machine for Phase 104.5 Always-On Daemon."""

from __future__ import annotations
import logging
import threading
import time
from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("jarvisx.presence")


class PresenceState(str, Enum):
    OFFLINE = "OFFLINE"
    BOOTING = "BOOTING"
    READY = "READY"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    EXECUTING = "EXECUTING"
    SLEEPING = "SLEEPING"
    ERROR_RECOVERY = "ERROR_RECOVERY"
    STOPPING = "STOPPING"


class InvalidPresenceTransitionError(Exception):
    """Raised when an illegal state machine transition is attempted."""
    pass


class PresenceStateMachine:
    """Enforces strict, validated state transitions for the always-on daemon."""

    # Valid transitions map: from_state -> {allowed_to_states}
    VALID_TRANSITIONS: Dict[PresenceState, Set[PresenceState]] = {
        PresenceState.OFFLINE: {PresenceState.BOOTING},
        PresenceState.BOOTING: {PresenceState.READY, PresenceState.ERROR_RECOVERY, PresenceState.STOPPING},
        PresenceState.READY: {
            PresenceState.LISTENING,
            PresenceState.PROCESSING,
            PresenceState.EXECUTING,
            PresenceState.SLEEPING,
            PresenceState.STOPPING,
            PresenceState.ERROR_RECOVERY,
        },
        PresenceState.LISTENING: {
            PresenceState.PROCESSING,
            PresenceState.READY,
            PresenceState.SLEEPING,
            PresenceState.STOPPING,
            PresenceState.ERROR_RECOVERY,
        },
        PresenceState.PROCESSING: {
            PresenceState.EXECUTING,
            PresenceState.READY,
            PresenceState.SLEEPING,
            PresenceState.STOPPING,
            PresenceState.ERROR_RECOVERY,
        },
        PresenceState.EXECUTING: {
            PresenceState.READY,
            PresenceState.SLEEPING,
            PresenceState.PROCESSING,
            PresenceState.STOPPING,
            PresenceState.ERROR_RECOVERY,
        },
        PresenceState.SLEEPING: {
            PresenceState.READY,
            PresenceState.LISTENING,
            PresenceState.PROCESSING,
            PresenceState.STOPPING,
            PresenceState.ERROR_RECOVERY,
        },
        PresenceState.ERROR_RECOVERY: {
            PresenceState.READY,
            PresenceState.SLEEPING,
            PresenceState.STOPPING,
            PresenceState.OFFLINE,
        },
        PresenceState.STOPPING: {PresenceState.OFFLINE},
    }

    def __init__(self, initial_state: PresenceState = PresenceState.OFFLINE):
        self._current_state = initial_state
        self._state_entered_at = time.time()
        self._history: List[Tuple[PresenceState, PresenceState, float]] = []
        self._listeners: List[Callable[[PresenceState, PresenceState], None]] = []
        self._lock = threading.Lock()

    @property
    def current_state(self) -> PresenceState:
        with self._lock:
            return self._current_state

    @property
    def time_in_current_state(self) -> float:
        with self._lock:
            return time.time() - self._state_entered_at

    def can_transition_to(self, target_state: PresenceState) -> bool:
        """Check if transition from current state to target state is legally allowed."""
        with self._lock:
            allowed = self.VALID_TRANSITIONS.get(self._current_state, set())
            return target_state in allowed

    def transition_to(self, target_state: PresenceState, reason: str = "") -> PresenceState:
        """Execute state transition with validation and listener notification."""
        with self._lock:
            if target_state == self._current_state:
                return self._current_state

            allowed = self.VALID_TRANSITIONS.get(self._current_state, set())
            if target_state not in allowed:
                err_msg = (
                    f"Illegal presence transition: cannot transition from '{self._current_state.value}' "
                    f"to '{target_state.value}'. Allowed targets: {[s.value for s in allowed]}"
                )
                logger.error(err_msg)
                raise InvalidPresenceTransitionError(err_msg)

            old_state = self._current_state
            self._current_state = target_state
            now = time.time()
            self._history.append((old_state, target_state, now))
            if len(self._history) > 100:
                self._history = self._history[-100:]
            self._state_entered_at = now

            logger.info(f"Presence transition: {old_state.value} -> {target_state.value} ({reason or 'standard'})")
            listeners = list(self._listeners)

        for listener in listeners:
            try:
                listener(old_state, target_state)
            except Exception as e:
                logger.error(f"Error in presence listener: {e}")

        return target_state

    def add_listener(self, listener: Callable[[PresenceState, PresenceState], None]):
        """Register a callback for state changes."""
        with self._lock:
            self._listeners.append(listener)

    def can_listen_voice(self) -> bool:
        """Check if microphone listening is safe in current state."""
        return self.current_state in (PresenceState.READY, PresenceState.SLEEPING, PresenceState.LISTENING)

    def can_execute_tools(self) -> bool:
        """Check if tool execution is safe in current state."""
        return self.current_state in (PresenceState.READY, PresenceState.PROCESSING, PresenceState.EXECUTING)
