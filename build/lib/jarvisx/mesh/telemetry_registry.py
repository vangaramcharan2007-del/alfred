"""
Next-Generation Worker Registry & Live AI Mesh Telemetry Engine for Jarvis X.

Architecture:
- Workers execute, Jarvis verifies.
- Auto-discovery of Ollama models via live /api/tags probing over Tailscale mesh.
- Real-time latency tracking, GPU/VRAM telemetry, and workload state machine (IDLE, BUSY, OFFLINE).
- Intelligent least-load / lowest-latency routing with automatic master fallback.
"""

from __future__ import annotations

import asyncio
import json
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class MeshNodeState(str, Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"


@dataclass
class MeshNodeTelemetry:
    worker_id: str
    name: str
    tailscale_ip: str
    port: int = 11434
    status: MeshNodeState = MeshNodeState.OFFLINE
    available_models: List[str] = field(default_factory=list)
    gpu_name: str = "Integrated / CPU"
    vram_used_gb: float = 0.0
    vram_total_gb: float = 0.0
    cpu_util_pct: float = 0.0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 16.0
    temperature_c: float = 45.0
    active_jobs: int = 0
    max_concurrent_jobs: int = 4
    current_job_id: Optional[str] = None
    last_heartbeat: float = 0.0
    latency_ms: float = 0.0
    is_master: bool = False

    @property
    def endpoint_url(self) -> str:
        clean_ip = self.tailscale_ip.replace("http://", "").replace("https://", "").rstrip("/")
        return f"http://{clean_ip}:{self.port}"

    @property
    def is_routable(self) -> bool:
        return self.status in (MeshNodeState.IDLE, MeshNodeState.BUSY) and self.active_jobs < self.max_concurrent_jobs

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MeshNodeTelemetry:
        d = data.copy()
        if "status" in d:
            try:
                d["status"] = MeshNodeState(d["status"])
            except Exception:
                d["status"] = MeshNodeState.OFFLINE
        return cls(**d)


class EnhancedWorkerRegistry:
    """Manages persistent mesh worker topologies, concurrent health probes, and smart routing."""

    DEFAULT_NODES = [
        MeshNodeTelemetry(
            worker_id="NANI-YOGA7I",
            name="NANI Master (Yoga 7i)",
            tailscale_ip="127.0.0.1",
            port=11434,
            gpu_name="Intel Arc Graphics (Meteor Lake)",
            vram_total_gb=8.8,
            ram_total_gb=16.0,
            is_master=True,
            max_concurrent_jobs=4,
        ),
        MeshNodeTelemetry(
            worker_id="LAB-01",
            name="ASUS TUF A16 (Lab Node)",
            tailscale_ip="100.77.90.36",
            port=11434,
            gpu_name="AMD Radeon RX 7600S / RTX",
            vram_total_gb=8.0,
            ram_total_gb=16.0,
            max_concurrent_jobs=2,
        ),
        MeshNodeTelemetry(
            worker_id="LAB-02",
            name="RTX 4050 GPU Node",
            tailscale_ip="100.81.36.31",
            port=11434,
            gpu_name="NVIDIA GeForce RTX 4050 (6GB)",
            vram_total_gb=6.0,
            ram_total_gb=16.0,
            max_concurrent_jobs=4,
        ),
        MeshNodeTelemetry(
            worker_id="LAB-03",
            name="ASUS TUF Cluster 3",
            tailscale_ip="100.94.12.88",
            port=11434,
            gpu_name="NVIDIA RTX Dedicated GPU",
            vram_total_gb=8.0,
            ram_total_gb=32.0,
            max_concurrent_jobs=4,
        ),
        MeshNodeTelemetry(
            worker_id="FRIEND-4060",
            name="Remote RTX 4060 Node",
            tailscale_ip="100.112.45.19",
            port=11434,
            gpu_name="NVIDIA GeForce RTX 4060 (8GB)",
            vram_total_gb=8.0,
            ram_total_gb=32.0,
            max_concurrent_jobs=4,
        ),
    ]

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("var/db/mesh_workers.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.workers: Dict[str, MeshNodeTelemetry] = {}
        self.load()

    def load(self) -> None:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.workers = {
                        w["worker_id"]: MeshNodeTelemetry.from_dict(w)
                        for w in data.get("workers", [])
                    }
            except Exception:
                self._load_defaults()
        else:
            self._load_defaults()

    def _load_defaults(self) -> None:
        self.workers = {node.worker_id: node for node in self.DEFAULT_NODES}
        self.save()

    def save(self) -> None:
        try:
            payload = {
                "workers": [w.to_dict() for w in self.workers.values()],
                "updated_at": time.time(),
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass

    def register_worker(self, node: MeshNodeTelemetry) -> None:
        """Register or overwrite an active worker node."""
        self.workers[node.worker_id] = node
        self.save()

    def register_or_update(
        self,
        worker_id: str,
        tailscale_ip: str,
        name: Optional[str] = None,
        port: int = 11434,
        gpu_name: Optional[str] = None,
        vram_total_gb: Optional[float] = None,
    ) -> MeshNodeTelemetry:

        worker = self.workers.get(worker_id)
        if not worker:
            worker = MeshNodeTelemetry(
                worker_id=worker_id,
                name=name or worker_id,
                tailscale_ip=tailscale_ip,
                port=port,
            )
            self.workers[worker_id] = worker
        else:
            worker.tailscale_ip = tailscale_ip
            worker.port = port
            if name:
                worker.name = name
            if gpu_name:
                worker.gpu_name = gpu_name
            if vram_total_gb:
                worker.vram_total_gb = vram_total_gb

        self.save()
        return worker

    async def probe_node(self, worker: MeshNodeTelemetry, timeout_sec: float = 1.5) -> MeshNodeTelemetry:
        """Probes a single node's Ollama /api/tags endpoint to measure latency and retrieve models."""
        start_t = time.time()
        url = f"{worker.endpoint_url}/api/tags"

        loop = asyncio.get_running_loop()

        def _do_http_probe():
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "JarvisX-Mesh-Prober/2.0"})
                with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                    if resp.status == 200:
                        return json.loads(resp.read().decode("utf-8"))
            except Exception:
                return None

        data = await loop.run_in_executor(None, _do_http_probe)
        latency = round((time.time() - start_t) * 1000, 1)

        if data and "models" in data:
            worker.status = MeshNodeState.BUSY if worker.active_jobs > 0 else MeshNodeState.IDLE
            worker.available_models = [m.get("name") for m in data.get("models", []) if m.get("name")]
            worker.last_heartbeat = time.time()
            worker.latency_ms = latency
        else:
            worker.status = MeshNodeState.OFFLINE
            worker.latency_ms = 999.0

        return worker

    async def probe_mesh_health(self, timeout_sec: float = 1.5) -> List[MeshNodeTelemetry]:
        """Probes all registered mesh nodes concurrently."""
        tasks = [self.probe_node(w, timeout_sec=timeout_sec) for w in self.workers.values()]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        self.save()
        return list(self.workers.values())

    def get_mesh_dashboard_text(self) -> str:
        """Formats the visual ASCII live dashboard requested for Jarvis X."""
        lines = [
            "=========================================================================================================",
            " 🌐 JARVIS X: DISTRIBUTED AI MESH TELEMETRY DASHBOARD",
            "=========================================================================================================",
            f"{'WORKER ID':<14} {'IP':<15} {'STATUS':<12} {'LATENCY':<10} {'LOAD':<8} {'MODELS':<40}",
            "---------------------------------------------------------------------------------------------------------",
        ]

        for w in self.workers.values():
            if w.status == MeshNodeState.IDLE:
                status_str = "🟢 IDLE"
            elif w.status == MeshNodeState.BUSY:
                status_str = "🟡 BUSY"
            elif w.status == MeshNodeState.DEGRADED:
                status_str = "🟠 DEGRADED"
            else:
                status_str = "🔴 OFFLINE"

            lat_str = f"{w.latency_ms}ms" if w.status != MeshNodeState.OFFLINE else "TIMEOUT"
            load_str = f"{w.active_jobs}/{w.max_concurrent_jobs}"
            models_str = ", ".join(w.available_models[:3])
            if len(w.available_models) > 3:
                models_str += f" (+{len(w.available_models)-3})"
            if not models_str:
                models_str = "-"

            lines.append(
                f"{w.worker_id:<14} {w.tailscale_ip:<15} {status_str:<12} {lat_str:<10} {load_str:<8} {models_str:<40}"
            )

        lines.append("=========================================================================================================")
        return "\n".join(lines)

    def route_inference_job(self, target_model: str, fallback_to_master: bool = True) -> Optional[MeshNodeTelemetry]:
        """
        Select the optimal node to execute an inference request.
        Priority:
        1. Node must be routable (ONLINE/IDLE/BUSY with available capacity).
        2. Node must possess the requested model (or model family prefix).
        3. Lowest load (active_jobs ascending).
        4. Lowest network latency (latency_ms ascending).
        """
        candidates: List[MeshNodeTelemetry] = []
        model_family = target_model.split(":")[0].lower()

        for w in self.workers.values():
            if not w.is_routable:
                continue
            has_model = any(model_family in m.lower() for m in w.available_models)
            if has_model:
                candidates.append(w)

        if candidates:
            # Sort by active_jobs, then latency
            candidates.sort(key=lambda n: (n.active_jobs, n.latency_ms))
            return candidates[0]

        # Fallback to local master if allowed
        if fallback_to_master:
            master = self.workers.get("NANI-YOGA7I")
            if master and master.is_routable:
                return master

        return None


_GLOBAL_ENHANCED_REGISTRY: Optional[EnhancedWorkerRegistry] = None


def get_enhanced_worker_registry() -> EnhancedWorkerRegistry:
    global _GLOBAL_ENHANCED_REGISTRY
    if _GLOBAL_ENHANCED_REGISTRY is None:
        _GLOBAL_ENHANCED_REGISTRY = EnhancedWorkerRegistry()
    return _GLOBAL_ENHANCED_REGISTRY
