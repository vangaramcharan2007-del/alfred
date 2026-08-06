"""Unit and Integration Tests for Phase 90: Alfred Sovereign Personal OS Grand Finale v100.0 Master Release.

Tests GrandFinaleReleaseEngine manifest generation, 7-layer verification, and kernel objectives.
"""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.runtime import GrandFinaleReleaseEngine


def test_grand_finale_release_manifest_generation():
    """Verify GrandFinaleReleaseEngine generates persistent v100.0 release manifest and verifies 7-layer audit."""
    kernel = PersonalOSKernel()
    engine = GrandFinaleReleaseEngine(manifest_dir="var/config")

    res = engine.execute_grand_finale_release(os_kernel=kernel)
    assert res["status"] == "GRAND_FINALE_COMPLETED"
    assert res["version"] == "v100.0"
    assert os.path.exists(res["manifest_file"])

    with open(res["manifest_file"], "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["version"] == "v100.0"
    assert data["status"] == "GRAND_FINALE_LOCKED"
    assert data["total_hspw_achieved"] >= 40.0
    assert len(data["architectural_layers_audit"]) == 7


def test_kernel_objective_routing_phase90():
    """Verify PersonalOSKernel routes grand finale master release objectives."""
    kernel = PersonalOSKernel()

    res = kernel.execute_objective("grand finale")
    assert res["status"] == "GRAND_FINALE_COMPLETED"
    assert res["version"] == "v100.0"
    assert res["milestone_locked"] is True
