"""Unit and Integration Tests for Phase 74: Native Windows System Tray + Hands-Free Voice Runtime.

Tests system tray service lifecycle, voice listener pipeline, command intent routing,
SQLite session recording, failure recovery, and architectural layer compliance.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.automation.real_voice_runtime import RealVoicePipeline
from jarvisx.automation.real_system_tray import RealSystemTray
from jarvisx.architecture import get_layer_for_module


def test_voice_pipeline_lifecycle_and_sqlite_recording():
    """Verify voice pipeline start/pause listening and SQLite memory recording."""
    voice = RealVoicePipeline()
    start_res = voice.start_listening()
    assert start_res["status"] == "active"
    assert voice.is_listening is True
    assert voice.sessions_count == 1

    pause_res = voice.pause_listening()
    assert pause_res["status"] == "paused"
    assert voice.is_listening is False

    # Verify SQLite memory recording
    recent_memories = voice.memory.search_memory("voice_session", top_k=5)
    assert len(recent_memories) >= 1


def test_voice_command_intent_routing():
    """Verify spoken voice phrases are correctly routed to canonical PersonalOSKernel objectives."""
    kernel = PersonalOSKernel()
    voice = kernel.real_voice
    voice.start_listening()

    # Test spoken voice command: "Alfred organize downloads"
    r1 = voice.process_spoken_phrase("Alfred organize downloads", os_kernel=kernel)
    assert r1["status"] == "completed"
    assert r1["command"] == "organize downloads"
    assert voice.commands_executed == 1

    # Test spoken voice command: "Alfred clean temporary files"
    r2 = voice.process_spoken_phrase("Alfred clean temporary files", os_kernel=kernel)
    assert r2["status"] == "completed"

    # Test spoken voice command: "Alfred show system status"
    r3 = voice.process_spoken_phrase("Alfred show system status", os_kernel=kernel)
    assert r3["status"] == "completed"

    assert voice.get_voice_telemetry()["voice_hspw"] >= 15.00


def test_voice_pipeline_failure_recovery():
    """Verify voice pipeline isolates errors and records failures cleanly in SQLite without crashing."""
    kernel = PersonalOSKernel()
    voice = kernel.real_voice
    voice.start_listening()

    # Intentionally pass invalid command that triggers handler failure
    class BrokenKernel:
        def execute_objective(self, req):
            raise RuntimeError("Microphone audio stream buffer overflow simulation")

    res = voice.process_spoken_phrase("Alfred break audio", os_kernel=BrokenKernel())
    assert res["status"] == "failed"
    assert voice.failures_count == 1

    # Verify voice pipeline remains active for subsequent commands
    assert voice.is_listening is True


def test_system_tray_lifecycle_and_menu_actions():
    """Verify native Windows system tray lifecycle, menu actions, and telemetry."""
    kernel = PersonalOSKernel()
    tray = kernel.real_tray

    start_res = tray.start_tray_service()
    assert start_res["status"] == "active"
    assert tray.is_active is True

    # Test tray menu action: start voice listener
    l_res = tray.action_start_listening()
    assert l_res["status"] == "active"

    # Test tray menu action: open dashboard
    dash_res = tray.action_open_dashboard()
    assert "status" in dash_res

    # Test tray menu action: safe shutdown
    stop_res = tray.action_shutdown_safely()
    assert stop_res["status"] == "stopped"
    assert tray.is_active is False
    assert tray.actions_count >= 3


def test_phase74_architectural_layer_compliance():
    """Verify Phase 74 submodules map cleanly to canonical Layer 4 (agents/automation)."""
    l_voice = get_layer_for_module("jarvisx.automation.real_voice_runtime")
    l_tray = get_layer_for_module("jarvisx.automation.real_system_tray")

    assert l_voice == "agents"
    assert l_tray == "agents"
