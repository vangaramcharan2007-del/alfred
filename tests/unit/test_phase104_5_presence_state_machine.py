"""Unit and Adversarial Test Suite for Phase 104.5 Presence State Machine & Resource Governor."""

import pytest
import time

from jarvisx.runtime.presence_state_machine import (
    InvalidPresenceTransitionError,
    PresenceState,
    PresenceStateMachine,
)
from jarvisx.runtime.resource_governor import ResourceGovernor


def test_valid_presence_state_lifecycle():
    """Verify happy-path state transitions from boot to sleep and execution."""
    sm = PresenceStateMachine(PresenceState.OFFLINE)
    assert sm.current_state == PresenceState.OFFLINE
    assert sm.can_listen_voice() is False
    assert sm.can_execute_tools() is False

    # 1. Booting
    sm.transition_to(PresenceState.BOOTING)
    assert sm.current_state == PresenceState.BOOTING

    # 2. Ready
    sm.transition_to(PresenceState.READY)
    assert sm.current_state == PresenceState.READY
    assert sm.can_listen_voice() is True
    assert sm.can_execute_tools() is True

    # 3. Listening -> Processing -> Executing -> Ready
    sm.transition_to(PresenceState.LISTENING)
    assert sm.current_state == PresenceState.LISTENING

    sm.transition_to(PresenceState.PROCESSING)
    assert sm.current_state == PresenceState.PROCESSING

    sm.transition_to(PresenceState.EXECUTING)
    assert sm.current_state == PresenceState.EXECUTING

    sm.transition_to(PresenceState.READY)
    assert sm.current_state == PresenceState.READY

    # 4. Sleeping
    sm.transition_to(PresenceState.SLEEPING)
    assert sm.current_state == PresenceState.SLEEPING
    assert sm.can_listen_voice() is True


def test_invalid_presence_state_transitions_rejected():
    """Verify strict rejection of illegal state machine transitions."""
    sm = PresenceStateMachine(PresenceState.OFFLINE)

    # Cannot jump directly to EXECUTING or LISTENING from OFFLINE
    with pytest.raises(InvalidPresenceTransitionError):
        sm.transition_to(PresenceState.EXECUTING)

    with pytest.raises(InvalidPresenceTransitionError):
        sm.transition_to(PresenceState.LISTENING)

    # Boot and move to STOPPING
    sm.transition_to(PresenceState.BOOTING)
    sm.transition_to(PresenceState.STOPPING)

    # Cannot transition to LISTENING or EXECUTING while STOPPING
    with pytest.raises(InvalidPresenceTransitionError):
        sm.transition_to(PresenceState.LISTENING)


def test_presence_state_listeners():
    """Verify callback notifications when presence state changes."""
    sm = PresenceStateMachine(PresenceState.OFFLINE)
    transitions_recorded = []

    def on_change(old_st, new_st):
        transitions_recorded.append((old_st, new_st))

    sm.add_listener(on_change)

    sm.transition_to(PresenceState.BOOTING)
    sm.transition_to(PresenceState.READY)

    assert len(transitions_recorded) == 2
    assert transitions_recorded[0] == (PresenceState.OFFLINE, PresenceState.BOOTING)
    assert transitions_recorded[1] == (PresenceState.BOOTING, PresenceState.READY)


def test_error_recovery_presence_cycle():
    """Verify system enters ERROR_RECOVERY and transitions back to READY."""
    sm = PresenceStateMachine(PresenceState.OFFLINE)
    sm.transition_to(PresenceState.BOOTING)
    sm.transition_to(PresenceState.ERROR_RECOVERY)
    assert sm.current_state == PresenceState.ERROR_RECOVERY

    # Recover to READY
    sm.transition_to(PresenceState.READY)
    assert sm.current_state == PresenceState.READY


def test_resource_governor_lazy_loading_and_eviction():
    """Verify heavy components are only loaded on-demand and evicted when idle."""
    gov = ResourceGovernor(max_idle_seconds=0.1)  # 100ms for test
    load_counts = {"whisper": 0, "embeddings": 0}

    def load_whisper():
        load_counts["whisper"] += 1
        return "LoadedWhisperModel"

    def load_embeddings():
        load_counts["embeddings"] += 1
        return "LoadedEmbeddingIndex"

    gov.register_lazy_component("whisper", load_whisper)
    gov.register_lazy_component("embeddings", load_embeddings)

    # Initially neither is loaded in RAM
    assert gov.is_loaded("whisper") is False
    assert gov.is_loaded("embeddings") is False
    assert load_counts["whisper"] == 0

    # Fetch whisper -> loads on demand
    w_model = gov.get_component("whisper")
    assert w_model == "LoadedWhisperModel"
    assert gov.is_loaded("whisper") is True
    assert gov.is_loaded("embeddings") is False
    assert load_counts["whisper"] == 1

    # Second fetch uses cached instance in RAM
    gov.get_component("whisper")
    assert load_counts["whisper"] == 1

    # Wait for idle timeout and evict
    time.sleep(0.15)
    evicted = gov.evict_idle_components()
    assert evicted == 1
    assert gov.is_loaded("whisper") is False
