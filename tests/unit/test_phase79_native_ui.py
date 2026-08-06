"""Unit and Integration Tests for Phase 79: Native Windows Desktop Companion UI & Toast Interactivity.

Tests NativeCompanionUI, InteractiveNotificationEngine, and kernel objective handlers.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.automation import NativeCompanionUI, InteractiveNotificationEngine


def test_native_companion_ui_lifecycle():
    """Verify NativeCompanionUI state synthesis, headless startup, and shutdown."""
    kernel = PersonalOSKernel()
    ui = NativeCompanionUI(os_kernel=kernel)

    stat = ui.build_status_dict()
    assert "voice_status" in stat
    assert "hspw" in stat
    assert "top_priority" in stat

    res_start = ui.start_widget(headless=True)
    assert res_start["status"] in ("HEADLESS_ACTIVE", "RUNNING")

    res_stop = ui.stop_widget()
    assert res_stop["status"] == "STOPPED"


def test_interactive_notification_confirmation():
    """Verify InteractiveNotificationEngine dispatches prompts and executes callbacks upon confirmation."""
    engine = InteractiveNotificationEngine()

    executed = {"flag": False}

    def dummy_callback():
        executed["flag"] = True
        return {"status": "SUCCESS"}

    dispatch = engine.send_interactive_confirmation(
        title="Clean Storage Confirmation",
        message="Low disk space. Purge temp files?",
        callback_action=dummy_callback,
    )

    assert dispatch["status"] == "PROMPT_DISPATCHED"
    conf_id = dispatch["conf_id"]
    assert conf_id in engine.pending_confirmations

    confirm = engine.confirm_action(conf_id)
    assert confirm["status"] == "CONFIRMED"
    assert executed["flag"] is True


def test_kernel_objective_routing_phase79():
    """Verify PersonalOSKernel routes widget and interactive alert objectives."""
    kernel = PersonalOSKernel()

    w_res = kernel.execute_objective("launch widget", headless=True)
    assert w_res["status"] in ("HEADLESS_ACTIVE", "RUNNING")

    a_res = kernel.execute_objective("interactive alert", title="Low Battery", message="Battery at 15%")
    assert a_res["status"] == "PROMPT_DISPATCHED"
