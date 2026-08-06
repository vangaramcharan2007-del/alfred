"""Unit and Integration Tests for Phase 82: Multi-Node Edge-Cloud Mesh & Remote Autopilot Synchronization.

Tests RemoteSyncEngine mesh synchronization, remote autopilot dispatch, and kernel objectives.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.adapters import RemoteSyncEngine


def test_remote_sync_engine_mesh_synchronization():
    """Verify RemoteSyncEngine registers mesh nodes and synchronizes memory records."""
    kernel = PersonalOSKernel()
    engine = RemoteSyncEngine()

    res = engine.sync_mesh_nodes(os_kernel=kernel)
    assert res["status"] == "SYNCED"
    assert res["nodes_synced"] == 2
    assert res["remote_hspw"] >= 8.5


def test_remote_autopilot_dispatch():
    """Verify RemoteSyncEngine dispatches remote autopilot workflows."""
    kernel = PersonalOSKernel()
    engine = RemoteSyncEngine()

    res = engine.dispatch_remote_autopilot("vps_cloud_node", "SYSTEM_DEEP_CLEAN", os_kernel=kernel)
    assert res["status"] == "DISPATCHED"
    assert res["target_node"] == "vps_cloud_node"
    assert res["execution_outcome"]["status"] == "COMPLETED"


def test_kernel_objective_routing_phase82():
    """Verify PersonalOSKernel routes remote sync and dispatch objectives."""
    kernel = PersonalOSKernel()

    s_res = kernel.execute_objective("remote sync")
    assert s_res["status"] == "SYNCED"

    d_res = kernel.execute_objective("dispatch remote autopilot", target_node="vps_cloud_node")
    assert d_res["status"] == "DISPATCHED"
