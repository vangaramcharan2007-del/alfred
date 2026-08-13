"""Worker Node Data Models and Persistent Registry for Jarvis X Distributed Mesh.

Manages network compute workers (e.g. friends' gaming laptops on Tailscale or LAN),
tracking their IP, GPU model, VRAM, live load, temperature, and supported LLM models.
"""

from __future__ import annotations
import os
import json
import time
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict


class WorkerStatus(str, Enum):
    ONLINE = "ONLINE"
    BUSY = "BUSY"
    GAMING = "GAMING"
    PAUSED = "PAUSED"
    OFFLINE = "OFFLINE"


@dataclass
class WorkerMetrics:
    gpu_name: str = "Unknown GPU"
    gpu_util_percent: float = 0.0
    vram_used_gb: float = 0.0
    vram_total_gb: float = 0.0
    cpu_util_percent: float = 0.0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    temperature_c: float = 0.0
    is_gaming: bool = False
    last_seen: float = 0.0


@dataclass
class WorkerNode:
    worker_id: str
    name: str
    host: str  # e.g. "100.101.102.103" or "192.168.1.50"
    port: int = 11434
    endpoint_type: str = "ollama"  # ollama or custom_api
    status: WorkerStatus = WorkerStatus.OFFLINE
    models: List[str] = field(default_factory=list)
    metrics: WorkerMetrics = field(default_factory=WorkerMetrics)
    max_gpu_threshold: float = 75.0  # Back off if GPU > 75%
    max_temp_threshold: float = 78.0 # Back off if Temp > 78°C
    priority: int = 10               # Higher priority chosen first
    total_tasks_completed: int = 0
    total_latency_ms: float = 0.0

    @property
    def url(self) -> str:
        clean_host = self.host.replace("http://", "").replace("https://", "").rstrip("/")
        if ":" in clean_host:
            return f"http://{clean_host}"
        return f"http://{clean_host}:{self.port}"

    @property
    def is_available(self) -> bool:
        if self.status != WorkerStatus.ONLINE:
            return False
        if self.metrics.is_gaming:
            return False
        if self.metrics.gpu_util_percent > self.max_gpu_threshold:
            return False
        if self.metrics.temperature_c > self.max_temp_threshold:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkerNode:
        data = data.copy()
        if "status" in data:
            try:
                data["status"] = WorkerStatus(data["status"])
            except Exception:
                data["status"] = WorkerStatus.OFFLINE
        if "metrics" in data and isinstance(data["metrics"], dict):
            data["metrics"] = WorkerMetrics(**data["metrics"])
        return cls(**data)


class WorkerRegistry:
    """Persistent registry storing and managing distributed mesh workers."""

    def __init__(self, storage_path: str = "var/workers.json"):
        self.storage_path = Path(storage_path)
        self.workers: Dict[str, WorkerNode] = {}
        self._ensure_storage()
        self.load()

    def _ensure_storage(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.save()

    def load(self) -> None:
        """Load workers from JSON file."""
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.workers = {
                    w["worker_id"]: WorkerNode.from_dict(w)
                    for w in data.get("workers", [])
                }
        except Exception:
            self.workers = {}

    def save(self) -> None:
        """Save workers to JSON file."""
        try:
            data = {"workers": [w.to_dict() for w in self.workers.values()], "updated_at": time.time()}
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def register_worker(self, name: str, host: str, port: int = 11434, models: Optional[List[str]] = None, priority: int = 10) -> WorkerNode:
        """Register or update a worker node."""
        worker_id = f"worker_{name.lower().replace(' ', '_')}"
        clean_host = host.replace("http://", "").replace("https://", "").strip()
        if ":" in clean_host:
            parts = clean_host.split(":")
            clean_host = parts[0]
            try:
                port = int(parts[1])
            except Exception:
                pass

        worker = WorkerNode(
            worker_id=worker_id,
            name=name,
            host=clean_host,
            port=port,
            models=models or ["qwen2.5-coder:7b", "llama3.2:latest", "qwen2.5:7b"],
            priority=priority,
            status=WorkerStatus.ONLINE
        )
        self.workers[worker_id] = worker
        self.save()
        return worker

    def remove_worker(self, worker_id: str) -> bool:
        """Remove a worker by ID or name."""
        target_id = worker_id
        if target_id not in self.workers:
            for wid, w in self.workers.items():
                if w.name.lower() == worker_id.lower():
                    target_id = wid
                    break
        if target_id in self.workers:
            del self.workers[target_id]
            self.save()
            return True
        return False

    def get_worker(self, worker_id: str) -> Optional[WorkerNode]:
        return self.workers.get(worker_id)

    def list_workers(self) -> List[WorkerNode]:
        return list(self.workers.values())

    def get_available_workers(self, model_name: Optional[str] = None) -> List[WorkerNode]:
        """Return available workers, sorted by load and priority."""
        available = [w for w in self.workers.values() if w.is_available]
        if model_name:
            # Filter workers that have the requested model or family
            model_prefix = model_name.split(":")[0].lower()
            matching = [
                w for w in available
                if any(model_prefix in m.lower() for m in w.models) or not w.models
            ]
            if matching:
                available = matching

        # Sort by: (1) GPU load ascending, (2) Temperature ascending, (3) Priority descending
        available.sort(key=lambda w: (w.metrics.gpu_util_percent, w.metrics.temperature_c, -w.priority))
        return available


_GLOBAL_WORKER_REGISTRY: Optional[WorkerRegistry] = None


def get_worker_registry() -> WorkerRegistry:
    global _GLOBAL_WORKER_REGISTRY
    if _GLOBAL_WORKER_REGISTRY is None:
        _GLOBAL_WORKER_REGISTRY = WorkerRegistry()
    return _GLOBAL_WORKER_REGISTRY
