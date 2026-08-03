import asyncio
import time
from jarvisx.memory.providers.sqlite_provider import SQLiteMemoryProvider
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.agents.capability_registry import CapabilityRegistry, AgentManifest
from jarvisx.nodes.node_registry import NodeRegistry
from jarvisx.nodes.worker_node import WorkerNode
from jarvisx.core.distributed_scheduler import DistributedScheduler
from jarvisx.agents.agent_monitor import AgentMonitor
from jarvisx.core.task_manager import TaskManager
from jarvisx.network.event_bus import DistributedEventBus
from jarvisx.core.recovery_manager import RecoveryManager
from jarvisx.core.logging import StructuredLogger

async def run_demo():
    print("\n--- COGNITIVE AGENT MESH DEMO ---")
    
    # 1. Initialize Components
    logger = StructuredLogger()
    memory_provider = SQLiteMemoryProvider()
    cognitive_memory = CognitiveMemory(memory_provider, logger=logger)
    
    cap_reg = CapabilityRegistry(logger=logger)
    node_reg = NodeRegistry(logger=logger)
    scheduler = DistributedScheduler(cap_reg, node_reg)
    agent_monitor = AgentMonitor(logger=logger)
    task_manager = TaskManager(logger=logger)
    event_bus = DistributedEventBus(logger=logger)
    
    recovery_manager = RecoveryManager(
        task_manager=task_manager,
        agent_monitor=agent_monitor,
        scheduler=scheduler,
        event_bus=event_bus,
        logger=logger
    )

    # 2. Setup Memory
    print("\n[COGNITIVE MEMORY] Extracting user preference...")
    mem_id = await cognitive_memory.extract_knowledge(
        subject="user.preference.compilation",
        fact="User prefers fast compile times over high optimization in dev builds.",
        confidence=0.95
    )
    print(f"-> Stored Semantic Memory: {mem_id}")
    
    print("[COGNITIVE MEMORY] Retrieving context for 'compile'...")
    results = await cognitive_memory.retrieve_context("compile")
    for r in results:
        print(f"-> Found Memory: {r['data']}")

    # 3. Setup Mesh Nodes
    print("\n[MESH] Initializing distributed nodes...")
    
    primary_node = WorkerNode(node_id="primary_node", name="Primary Node", hardware_info={"gpu": True})
    primary_node.register_agent("compiler_agent")
    
    backup_node = WorkerNode(node_id="backup_node", name="Backup Node", hardware_info={"gpu": False})
    backup_node.register_agent("compiler_agent")
    
    node_reg.register_node(primary_node)
    node_reg.register_node(backup_node)
    
    cap_reg.register_agent(AgentManifest(
        id="compiler_agent", 
        name="Compiler", 
        role="Build Engineer", 
        capabilities=["compiling", "building"],
        status="active"
    ))

    # Mark both online via monitor
    agent_monitor.register_heartbeat("compiler_agent", "primary_node")
    agent_monitor.register_heartbeat("compiler_agent", "backup_node")
    
    # Mark primary_node offline explicitly or simulate via failure
    # Wait, the failure is node disconnecting.

    # 4. Dispatch a Task
    print("\n[SCHEDULER] Dispatching task to primary node...")
    # Add dummy task manually via TaskManager to simulate dispatching
    task_id = "task_compile_123"
    task_manager.create_task(task_id, node="primary_node", agent="compiler_agent", trace_id="demo")
    task_manager.update_status(task_id, "RUNNING")
    
    print(f"-> Task {task_id} running on primary_node.")

    # 5. Simulate Failure and Recovery
    print("\n[RECOVERY] Simulating node failure on primary_node...")
    # Mark the node offline in the monitor so the scheduler won't pick it
    agent_monitor.monitor_node("primary_node", status="offline", latency=0)
    
    # We publish an event on the bus
    await event_bus.publish("agent.connection.disconnected", {"node_id": "primary_node"})
    
    # Allow event loop to process event
    await asyncio.sleep(0.5)
    
    task_status = task_manager.get_task(task_id)
    print(f"-> After recovery, task {task_id} status is: {task_status['status']}")
    print(f"-> Task is now assigned to node: {task_status['node']}")
    if task_status['node'] == 'backup_node':
        print("\nSUCCESS: Recovery Manager successfully migrated the task to backup_node!")
    else:
        print("\nFAILURE: Task was not migrated.")

if __name__ == "__main__":
    asyncio.run(run_demo())
