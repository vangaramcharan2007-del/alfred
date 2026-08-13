"""Unit tests for Jarvis X Distributed Worker Mesh Subsystem."""

import pytest
import asyncio
from jarvisx.mesh.worker_node import WorkerRegistry, WorkerNode, WorkerStatus, WorkerMetrics
from jarvisx.mesh.worker_router import WorkerMeshRouter
from jarvisx.mesh.worker_heartbeat import WorkerHeartbeatProber


def test_worker_registry_lifecycle(tmp_path):
    storage = str(tmp_path / "test_workers.json")
    reg = WorkerRegistry(storage_path=storage)

    # Register worker
    w = reg.register_worker(name="Gaming-4060", host="100.101.102.103", port=11434, models=["qwen2.5-coder:7b", "llama3:latest"])
    assert w.worker_id == "worker_gaming-4060"
    assert w.url == "http://100.101.102.103:11434"

    # Query
    loaded = reg.get_worker("worker_gaming-4060")
    assert loaded is not None
    assert loaded.name == "Gaming-4060"

    # Remove
    assert reg.remove_worker("Gaming-4060") is True
    assert reg.get_worker("worker_gaming-4060") is None


def test_worker_gaming_and_load_backoff(tmp_path):
    storage = str(tmp_path / "test_workers.json")
    reg = WorkerRegistry(storage_path=storage)

    w1 = reg.register_worker(name="Friend-A", host="100.1.1.1")
    w2 = reg.register_worker(name="Friend-B", host="100.1.1.2")

    # Friend A is idle
    w1.status = WorkerStatus.ONLINE
    w1.metrics.gpu_util_percent = 25.0
    w1.metrics.temperature_c = 55.0

    # Friend B is playing GTA (gaming detected)
    w2.status = WorkerStatus.GAMING
    w2.metrics.is_gaming = True

    avail = reg.get_available_workers()
    assert len(avail) == 1
    assert avail[0].name == "Friend-A"

    # Now Friend A GPU jumps to 90% (over limit)
    w1.metrics.gpu_util_percent = 92.0
    avail2 = reg.get_available_workers()
    assert len(avail2) == 0  # Both backed off!


def test_mesh_router_fallback(tmp_path):
    storage = str(tmp_path / "test_workers.json")
    reg = WorkerRegistry(storage_path=storage)
    router = WorkerMeshRouter(registry=reg)

    assert router.has_active_workers() is False

    res = asyncio.run(router.execute_mesh_inference("Hello"))
    assert res["status"] == "NOT_AVAILABLE"
    assert res["fallback_used"] is True
