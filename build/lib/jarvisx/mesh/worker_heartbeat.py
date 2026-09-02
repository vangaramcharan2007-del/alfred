"""Worker Heartbeat Monitor and Health Prober for Jarvis X Mesh.

Periodically queries worker endpoints over Tailscale / LAN to:
1. Verify online connectivity & measure network round-trip latency.
2. Synchronize installed LLM model catalogs.
3. Ingest GPU metrics (utilization, VRAM, temperature, gaming status).
4. Update worker online/offline states in the registry.
"""

from __future__ import annotations
import json
import time
import asyncio
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from jarvisx.mesh.worker_node import WorkerRegistry, WorkerNode, WorkerStatus, get_worker_registry


class WorkerHeartbeatProber:
    """Probes remote workers over network and updates status."""

    def __init__(self, registry: Optional[WorkerRegistry] = None):
        self.registry = registry or get_worker_registry()

    async def probe_worker(self, worker: WorkerNode, timeout_sec: float = 2.0) -> Dict[str, Any]:
        """Probe a single worker node over HTTP."""
        start_t = time.time()
        tags_url = f"{worker.url}/api/tags"

        try:
            loop = asyncio.get_running_loop()
            
            def _http_get():
                req = urllib.request.Request(tags_url, headers={"User-Agent": "JarvisX-Mesh/1.0"})
                with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                    if resp.status == 200:
                        return json.loads(resp.read().decode("utf-8"))
                return None

            data = await loop.run_in_executor(None, _http_get)

            if data and "models" in data:
                latency_ms = round((time.time() - start_t) * 1000, 1)
                installed_models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                
                worker.status = WorkerStatus.ONLINE
                worker.models = installed_models
                worker.metrics.last_seen = time.time()

                return {
                    "worker_id": worker.worker_id,
                    "name": worker.name,
                    "status": "ONLINE",
                    "latency_ms": latency_ms,
                    "models": installed_models,
                    "url": worker.url
                }
        except Exception as e:
            worker.status = WorkerStatus.OFFLINE
            return {
                "worker_id": worker.worker_id,
                "name": worker.name,
                "status": "OFFLINE",
                "error": str(e),
                "url": worker.url
            }

    async def probe_all_workers(self, timeout_sec: float = 2.5) -> List[Dict[str, Any]]:
        """Probe all registered workers concurrently."""
        workers = self.registry.list_workers()
        if not workers:
            return []

        tasks = [self.probe_worker(w, timeout_sec=timeout_sec) for w in workers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Save updated status to disk
        self.registry.save()

        processed = []
        for res in results:
            if isinstance(res, dict):
                processed.append(res)
            elif isinstance(res, Exception):
                processed.append({"status": "ERROR", "error": str(res)})
        return processed

    def update_worker_telemetry(self, worker_id: str, telemetry: Dict[str, Any]) -> bool:
        """Receive rich telemetry pushed from a Jarvis Worker Agent."""
        worker = self.registry.get_worker(worker_id)
        if not worker:
            return False

        m = worker.metrics
        m.gpu_name = telemetry.get("gpu_name", m.gpu_name)
        m.gpu_util_percent = float(telemetry.get("gpu_util_percent", m.gpu_util_percent))
        m.vram_used_gb = float(telemetry.get("vram_used_gb", m.vram_used_gb))
        m.vram_total_gb = float(telemetry.get("vram_total_gb", m.vram_total_gb))
        m.cpu_util_percent = float(telemetry.get("cpu_util_percent", m.cpu_util_percent))
        m.ram_used_gb = float(telemetry.get("ram_used_gb", m.ram_used_gb))
        m.ram_total_gb = float(telemetry.get("ram_total_gb", m.ram_total_gb))
        m.temperature_c = float(telemetry.get("temperature_c", m.temperature_c))
        m.is_gaming = bool(telemetry.get("is_gaming", m.is_gaming))
        m.last_seen = time.time()

        if m.is_gaming:
            worker.status = WorkerStatus.GAMING
        elif m.gpu_util_percent > worker.max_gpu_threshold or m.temperature_c > worker.max_temp_threshold:
            worker.status = WorkerStatus.BUSY
        else:
            worker.status = WorkerStatus.ONLINE

        self.registry.save()
        return True


_GLOBAL_HEARTBEAT_PROBER: Optional[WorkerHeartbeatProber] = None


def get_worker_heartbeat_prober() -> WorkerHeartbeatProber:
    global _GLOBAL_HEARTBEAT_PROBER
    if _GLOBAL_HEARTBEAT_PROBER is None:
        _GLOBAL_HEARTBEAT_PROBER = WorkerHeartbeatProber()
    return _GLOBAL_HEARTBEAT_PROBER
