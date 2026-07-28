import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional

from jarvisx.network.agent_protocol import (
    Envelope, 
    TaskRequest, 
    TaskAccepted, 
    TaskProgress, 
    TaskCompleted, 
    TaskFailed,
    TransportInterface
)
from jarvisx.core.logging import StructuredLogger

class WorkerRuntime:
    """
    Lightweight runtime executing on remote machines.
    Connects to the Alfred Gateway, processes tasks, and streams progress.
    """
    def __init__(self, node_id: str, secret_key: str, transport: TransportInterface, logger: Optional[StructuredLogger] = None):
        self.node_id = node_id
        self.secret_key = secret_key
        self.transport = transport
        self.logger = logger or StructuredLogger()
        
        self.capabilities: List[str] = []
        self._running = False

    def register_capability(self, capability: str):
        if capability not in self.capabilities:
            self.capabilities.append(capability)

    async def start(self):
        """Starts the main worker loop."""
        self._running = True
        self.logger.write("info", "worker.started", node=self.node_id)
        
        # In a real system, we would first send an Auth message and wait for an Ack.
        # Then register capabilities.
        
        # Start heartbeat and message loop
        asyncio.create_task(self._heartbeat_loop())
        await self._message_loop()

    async def stop(self):
        self._running = False

    async def _heartbeat_loop(self):
        while self._running:
            # We would send a heartbeat envelope here
            await asyncio.sleep(5)

    async def _message_loop(self):
        while self._running:
            try:
                # Reverse perspective: for the worker, rx/tx logic in transport is flipped
                # because the MockTransport handles both ends, the worker should use receive_message
                # but wait, MockTransport logic is hardcoded to Gateway perspective right now.
                # I'll just simulate it: the Gateway pushes to tx, Worker pulls from tx.
                # Actually, I'll need a bi-directional queue setup where the worker has a reference to the same MockTransport.
                # In MockTransport:
                # tx = Gateway to Node
                # rx = Node to Gateway
                
                # So the worker reads from tx:
                if self.node_id in getattr(self.transport, "queues", {}):
                    tx, rx = getattr(self.transport, "queues")[self.node_id]
                    msg = await tx.get()
                    await self._handle_message(msg, rx)
                else:
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.write("error", "worker.loop_error", error=str(e))
                await asyncio.sleep(1)

    async def _handle_message(self, msg: Envelope, rx: asyncio.Queue):
        if msg.type == "task.request":
            req_data = msg.payload
            
            # Send TaskAccepted
            accepted = TaskAccepted(task_id=req_data["task_id"], node_id=self.node_id, timestamp=str(time.time()))
            await rx.put(Envelope(
                message_id=f"msg_{uuid.uuid4().hex[:8]}",
                trace_id=msg.trace_id,
                timestamp=str(time.time()),
                type="task.accepted",
                payload=accepted.to_dict()
            ))
            
            # Spawn execution
            asyncio.create_task(self._execute_task(req_data, msg.trace_id, rx))

    async def _execute_task(self, req_data: Dict[str, Any], trace_id: str, rx: asyncio.Queue):
        task_id = req_data["task_id"]
        try:
            # Simulate progress steps
            for progress in [10, 40, 75]:
                await asyncio.sleep(0.05)
                prog_msg = TaskProgress(task_id=task_id, progress=progress, message="Processing", current_stage="running")
                await rx.put(Envelope(
                    message_id=f"msg_{uuid.uuid4().hex[:8]}",
                    trace_id=trace_id,
                    timestamp=str(time.time()),
                    type="task.progress",
                    payload=prog_msg.to_dict()
                ))
            
            # Complete
            await asyncio.sleep(0.05)
            comp_msg = TaskCompleted(task_id=task_id, status="completed", result={"rendered": True})
            await rx.put(Envelope(
                message_id=f"msg_{uuid.uuid4().hex[:8]}",
                trace_id=trace_id,
                timestamp=str(time.time()),
                type="task.completed",
                payload=comp_msg.to_dict()
            ))
            
        except Exception as e:
            fail_msg = TaskFailed(task_id=task_id, error=str(e), recoverable=False)
            await rx.put(Envelope(
                message_id=f"msg_{uuid.uuid4().hex[:8]}",
                trace_id=trace_id,
                timestamp=str(time.time()),
                type="task.failed",
                payload=fail_msg.to_dict()
            ))
