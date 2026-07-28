import asyncio
import time
import uuid

from jarvisx.network.gateway import AgentGateway, MockTransport
from jarvisx.nodes.worker_runtime import WorkerRuntime
from jarvisx.network.agent_protocol import Envelope
from jarvisx.core.task_manager import TaskManager
from jarvisx.memory.shared_memory import SharedMemory, MockSQLiteProvider
from jarvisx.network.event_bus import DistributedEventBus

async def run_demo():
    print('User: "Render this video"')
    print('Alfred: Searching capabilities...')
    await asyncio.sleep(0.5)
    print('Found: Editing Agent')
    
    print('Searching nodes...')
    await asyncio.sleep(0.5)
    print('Found: Gaming Laptop')
    
    print('Connecting...')
    
    # Setup Infrastructure
    transport = MockTransport()
    gateway = AgentGateway(transport)
    worker = WorkerRuntime("gaming_laptop", "secret", transport)
    
    tx = asyncio.Queue()
    rx = asyncio.Queue()
    transport.register_queues("gaming_laptop", tx, rx)
    
    # Event Bus & Task Manager
    bus = DistributedEventBus()
    task_manager = TaskManager()
    
    # Shared Memory
    memory_provider = MockSQLiteProvider()
    shared_memory = SharedMemory(memory_provider)
    
    # Connect
    await gateway.connect_node("gaming_laptop", "conn_123")
    print('Node authenticated')
    
    # Start worker background loop
    worker_task = asyncio.create_task(worker.start())
    
    # Gateway listens for messages
    async def gateway_listener():
        while True:
            msg = await gateway.receive_message("gaming_laptop")
            if msg:
                if msg.type == "task.progress":
                    prog = msg.payload.get('progress')
                    print(f"Progress: {prog}%")
                    task_manager.update_status(msg.payload['task_id'], "RUNNING", progress=prog)
                    await bus.publish("task.progress", msg.payload)
                elif msg.type == "task.completed":
                    print("Task completed")
                    task_manager.update_status(msg.payload['task_id'], "COMPLETED")
                    await bus.publish("task.completed", msg.payload)
                    break
            await asyncio.sleep(0.1)
            
    gateway_task = asyncio.create_task(gateway_listener())
    
    # Dispatch Task
    job_id = "job_123"
    task_manager.create_task(job_id, "gaming_laptop", "editing_agent", "trace_demo")
    print(f'Task created: {job_id}')
    
    req_msg = Envelope(
        message_id=f"msg_{uuid.uuid4().hex[:8]}",
        trace_id="trace_demo",
        timestamp=str(time.time()),
        type="task.request",
        payload={
            "task_id": job_id,
            "trace_id": "trace_demo",
            "agent_id": "editing_agent",
            "required_capabilities": ["video_editing"],
            "payload": {"video": "demo.mp4"},
            "priority": 5,
            "deadline": None
        }
    )
    await gateway.send_message("gaming_laptop", req_msg)
    
    # Wait for completion
    await gateway_task
    
    print('Updating shared memory...')
    await shared_memory.store_memory(job_id, {"status": "completed", "video": "demo_rendered.mp4"})
    
    # Clean up
    await worker.stop()
    worker_task.cancel()

if __name__ == "__main__":
    asyncio.run(run_demo())
