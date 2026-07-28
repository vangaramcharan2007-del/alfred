import pytest
import asyncio
from jarvisx.nodes.worker_runtime import WorkerRuntime
from jarvisx.network.gateway import MockTransport
from jarvisx.network.agent_protocol import Envelope

@pytest.mark.asyncio
async def test_worker_runtime_task_processing():
    transport = MockTransport()
    worker = WorkerRuntime("node1", "secret", transport)
    
    tx = asyncio.Queue()
    rx = asyncio.Queue()
    transport.register_queues("node1", tx, rx)
    
    # Send a task request
    req_msg = Envelope(
        message_id="msg1",
        trace_id="tr1",
        timestamp="100",
        type="task.request",
        payload={
            "task_id": "job_1",
            "trace_id": "tr1",
            "agent_id": "editing_agent",
            "required_capabilities": [],
            "payload": {},
            "priority": 5,
            "deadline": None
        }
    )
    await tx.put(req_msg)
    
    # Process single message manually for testing instead of full loop
    msg = await tx.get()
    await worker._handle_message(msg, rx)
    
    # Should get accepted
    accepted = await rx.get()
    assert accepted.type == "task.accepted"
    
    # Need to wait for async execution
    await asyncio.sleep(0.3)
    
    # Check progress
    msgs = []
    while not rx.empty():
        msgs.append(await rx.get())
        
    types = [m.type for m in msgs]
    assert "task.progress" in types
    assert "task.completed" in types
