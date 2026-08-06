"""Unit and Integration Tests for F.R.I.D.A.Y. Tactical Mode Persona & HUD Theme Controller.

Tests FridayTacticalMode tactical sweeps, HUD theme profiles, and kernel objectives.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.automation import FridayTacticalMode


def test_friday_tactical_mode_sweep():
    """Verify FridayTacticalMode executes screen & micro-swarm tactical sweeps."""
    kernel = PersonalOSKernel()
    mode = FridayTacticalMode(theme="CYAN_HOLOGRAPHIC_TACTICAL")

    res = mode.activate_tactical_sweep(os_kernel=kernel)
    assert res["status"] == "FRIDAY_TACTICAL_ACTIVE"
    assert res["persona"] == "F.R.I.D.A.Y."
    assert "tactical_response" in res
    assert res["friday_hspw"] >= 12.0


def test_kernel_objective_routing_friday_mode():
    """Verify PersonalOSKernel routes F.R.I.D.A.Y. tactical mode objectives."""
    kernel = PersonalOSKernel()

    res = kernel.execute_objective("friday mode")
    assert res["status"] == "FRIDAY_TACTICAL_ACTIVE"
    assert res["persona"] == "F.R.I.D.A.Y."
