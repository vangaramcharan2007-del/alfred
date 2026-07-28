import time
import asyncio
import uuid
from typing import List, Dict, Any, Optional

from jarvisx.network.agent_protocol import TaskRequest, TaskCompleted, TaskFailed
from jarvisx.core.logging import StructuredLogger

class WorkerNode:
    """
    Represents a machine capable of running agents.
    Provides async execution and health reporting.
    """
    def __init__(self, node_id: str, name: str, hardware_info: Dict[str, Any], logger: Optional[StructuredLogger] = None):
        self.node_id = node_id
        self.name = name
        self.status = "online"
        self.hardware_info = hardware_info
        self.available_agents: List[str] = []
        self.network_latency = 0
        self.logger = logger or StructuredLogger()
        self._last_heartbeat = time.time()
        self._active_jobs: Dict[str, asyncio.Task] = {}
        self._completed_jobs: Dict[str, Any] = {}

    def register_agent(self, agent_id: str) -> None:
        """Register an agent capability on this node."""
        if agent_id not in self.available_agents:
            self.available_agents.append(agent_id)
            self.logger.write("info", "worker.agent_registered", node=self.node_id, agent=agent_id)

    def heartbeat(self, latency: int = 0) -> None:
        """Update node heartbeat and network latency."""
        self._last_heartbeat = time.time()
        self.network_latency = latency
        self.status = "online"

    def get_status(self) -> Dict[str, Any]:
        """Get the current node status."""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "status": self.status,
            "agents": self.available_agents,
            "hardware": self.hardware_info,
            "latency": self.network_latency
        }

    async def execute_task(self, request: TaskRequest) -> str:
        """
        Accepts a TaskRequest and starts execution asynchronously.
        Returns a unique job_id immediately without blocking.
        """
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        self.logger.write("info", "worker.task_accepted", node=self.node_id, job=job_id, task=request.task_id)
        
        # In a real distributed system, we would send this over network.
        # Here we simulate an async background job executing the task.
        task = asyncio.create_task(self._mock_execution_worker(job_id, request))
        self._active_jobs[job_id] = task
        
        return job_id

    async def _mock_execution_worker(self, job_id: str, request: TaskRequest) -> None:
        """Internal mock worker for simulating asynchronous task completion."""
        try:
            # Simulate processing time based on priority
            await asyncio.sleep(0.1)
            
            response = TaskCompleted(
                task_id=request.task_id,
                status="completed",
                result={"status": "success", "executed_on": self.node_id}
            )
        except Exception as e:
            response = TaskFailed(
                task_id=request.task_id,
                error=str(e)
            )
            
        self._completed_jobs[job_id] = response
        if job_id in self._active_jobs:
            del self._active_jobs[job_id]
        
        # self.logger.write("info", "worker.task_completed", node=self.node_id, job=job_id, status=getattr(response, "status", "failed"))

    async def poll_job(self, job_id: str) -> Optional[Any]:
        """Retrieve completed job response, or None if still processing."""
        return self._completed_jobs.get(job_id)
