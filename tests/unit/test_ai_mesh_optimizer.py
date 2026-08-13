"""Unit tests for AIMeshOptimizer in Jarvis X."""

import pytest
import asyncio
from jarvisx.mesh.worker_node import WorkerRegistry, WorkerNode, WorkerStatus
from jarvisx.mesh.ai_mesh_optimizer import AIMeshOptimizer


def test_ai_task_classification():
    opt = AIMeshOptimizer()

    # 1. Local NPU classification
    res_hi = opt.classify_task_tier("hi")
    assert res_hi["tier"] == "LOCAL_NPU"
    assert res_hi["recommended_model"] == "qwen2.5-coder:1.5b"

    # 2. Parallel decomposition classification
    res_fullstack = opt.classify_task_tier("build a fullstack app with frontend and backend")
    assert res_fullstack["tier"] == "PARALLEL_DECOMPOSE"

    # 3. Deep coder classification
    res_algo = opt.classify_task_tier("explain Dijkstra algorithm and optimize it in Python")
    assert res_algo["tier"] == "DEEP_CODER_WORKER"


def test_ai_mesh_optimizer_singleton():
    from jarvisx.mesh.ai_mesh_optimizer import get_ai_mesh_optimizer
    opt1 = get_ai_mesh_optimizer()
    opt2 = get_ai_mesh_optimizer()
    assert opt1 is opt2
