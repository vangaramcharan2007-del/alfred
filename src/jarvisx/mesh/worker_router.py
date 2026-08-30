"""Distributed Worker Mesh Router and Load Balancer for Jarvis X.

Dispatches LLM prompts across network compute workers (e.g. friends' RTX gaming laptops).
Features:
- Dynamic node selection (least GPU load, lowest temperature, highest capability).
- Automatic task failover across worker pool.
- Seamless conversion to Ollama / OpenAI API format.
- Zero local CPU/GPU load on your main laptop.
"""

from __future__ import annotations
import json
import time
import asyncio
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from jarvisx.mesh.worker_node import WorkerRegistry, WorkerNode, WorkerStatus, get_worker_registry


class WorkerMeshRouter:
    """Intelligent load-balancing router for distributed mesh compute nodes."""

    def __init__(self, registry: Optional[WorkerRegistry] = None):
        self.registry = registry or get_worker_registry()

    def has_active_workers(self) -> bool:
        """Check if any remote mesh worker is currently registered and available."""
        return len(self.registry.get_available_workers()) > 0

    async def execute_mesh_inference(
        self,
        prompt: str,
        model: Optional[str] = None,
        conversation: Optional[List[Dict[str, str]]] = None,
        timeout_sec: float = 2.0
    ) -> Dict[str, Any]:

        """Dispatch inference request to the optimal available remote mesh worker."""
        available_workers = self.registry.get_available_workers(model_name=model)
        
        if not available_workers:
            return {
                "status": "NOT_AVAILABLE",
                "error": "No remote mesh workers currently available or all nodes busy/gaming.",
                "fallback_used": True
            }

        start_t = time.time()
        last_error = ""

        # Try workers in order of best load/capability
        for worker in available_workers:
            chosen_model = model or (worker.models[0] if worker.models else "qwen2.5-coder:7b")
            # If requested model is not on worker, pick first available model on worker
            if model and worker.models and model not in worker.models:
                # Find matching prefix
                prefix = model.split(":")[0]
                matches = [m for m in worker.models if prefix in m]
                if matches:
                    chosen_model = matches[0]
                else:
                    chosen_model = worker.models[0]

            print(f"[MESH COMPUTE] Offloading task to Worker '{worker.name}' ({worker.url}) | Model: {chosen_model}")

            try:
                loop = asyncio.get_running_loop()
                
                def _send_request():
                    url = f"{worker.url}/api/generate"
                    payload = {
                        "model": chosen_model,
                        "prompt": prompt,
                        "stream": False
                    }
                    if conversation:
                        payload["context_history"] = conversation[-10:]
                    
                    data = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                        if resp.status == 200:
                            return json.loads(resp.read().decode("utf-8"))
                    return None

                res_data = await loop.run_in_executor(None, _send_request)

                if res_data and "response" in res_data:
                    response_text = res_data.get("response", "")
                    latency_sec = round(time.time() - start_t, 3)
                    latency_ms = round(latency_sec * 1000, 1)

                    # Update worker statistics
                    worker.total_tasks_completed += 1
                    worker.total_latency_ms += latency_ms
                    worker.status = WorkerStatus.ONLINE
                    self.registry.save()

                    return {
                        "status": "AVAILABLE",
                        "provider_id": f"mesh.{worker.worker_id}",
                        "worker_name": worker.name,
                        "worker_url": worker.url,
                        "model": chosen_model,
                        "response": response_text,
                        "latency": latency_sec,
                        "latency_ms": latency_ms,
                        "tokens_generated": len(response_text.split()),
                        "fallback_used": False
                    }

            except Exception as e:
                last_error = f"Worker '{worker.name}' failed: {e}"
                print(f"[MESH COMPUTE] {last_error}. Trying next worker...")
                # Temporarily flag worker if connection refused
                if "refused" in str(e).lower() or "timed out" in str(e).lower():
                    worker.status = WorkerStatus.OFFLINE
                    self.registry.save()

        return {
            "status": "NOT_AVAILABLE",
            "error": f"All mesh workers failed. Last error: {last_error}",
            "fallback_used": True
        }


_GLOBAL_MESH_ROUTER: Optional[WorkerMeshRouter] = None


def get_worker_mesh_router() -> WorkerMeshRouter:
    global _GLOBAL_MESH_ROUTER
    if _GLOBAL_MESH_ROUTER is None:
        _GLOBAL_MESH_ROUTER = WorkerMeshRouter()
    return _GLOBAL_MESH_ROUTER
