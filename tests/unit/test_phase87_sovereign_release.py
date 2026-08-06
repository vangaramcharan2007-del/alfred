"""Unit and Integration Tests for Phase 87: Sovereign PC Operations & Production Milestone Lock Engine.

Tests SovereignReleaseManager release manifest generation, milestone lock, and kernel objectives.
"""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.runtime import SovereignReleaseManager


def test_sovereign_release_manager_manifest_generation():
    """Verify SovereignReleaseManager generates persistent release manifest and verifies milestone lock."""
    kernel = PersonalOSKernel()
    manager = SovereignReleaseManager(manifest_dir="var/test_config")

    res = manager.generate_release_manifest(os_kernel=kernel)
    assert res["status"] == "AUDITED_AND_LOCKED"
    assert res["version"] == "v87.0"
    assert os.path.exists(res["manifest_file"])

    with open(res["manifest_file"], "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["version"] == "v87.0"
    assert data["total_hspw_achieved"] >= 40.0
    assert data["milestone_passed"] is True


def test_kernel_objective_routing_phase87():
    """Verify PersonalOSKernel routes sovereign release audit objectives."""
    kernel = PersonalOSKernel()

    res = kernel.execute_objective("sovereign audit")
    assert res["status"] == "AUDITED_AND_LOCKED"
    assert res["milestone_locked"] is True
