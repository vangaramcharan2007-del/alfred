"""Unit tests for MeshBenchmarker in Jarvis X."""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from jarvisx.mesh.worker_node import WorkerRegistry, WorkerNode, WorkerStatus
from jarvisx.mesh.mesh_benchmarker import MeshBenchmarker


@pytest.mark.asyncio
async def test_mesh_benchmarker_structure(tmp_path):
    storage = str(tmp_path / "test_workers.json")
    reg = WorkerRegistry(storage_path=storage)
    bench = MeshBenchmarker(registry=reg)

    with patch("jarvisx.llm.ollama_provider.OllamaLLMProvider.generate", return_value={"status": "AVAILABLE", "response": "def quicksort(): pass"}):
        res = await bench.run_comparative_benchmark()
        assert "local_baseline" in res
        assert "remote_mesh" in res
        assert res["remote_mesh"]["status"] == "NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_mesh_benchmarker_with_mock_worker(tmp_path):
    storage = str(tmp_path / "test_workers.json")
    reg = WorkerRegistry(storage_path=storage)
    w = reg.register_worker(name="Mock-4060", host="127.0.0.1", port=19999)
    w.status = WorkerStatus.ONLINE

    bench = MeshBenchmarker(registry=reg)
    with patch("jarvisx.llm.ollama_provider.OllamaLLMProvider.generate", return_value={"status": "AVAILABLE", "response": "quicksort code"}):
        res = await bench.run_comparative_benchmark(target_worker_id=w.worker_id)
        assert res["remote_mesh"]["worker_name"] == "Mock-4060"
        assert "FAILED" in res["remote_mesh"]["status"] or "NOT_AVAILABLE" in res["remote_mesh"]["status"]
