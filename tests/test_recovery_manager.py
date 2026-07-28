import pytest
from jarvisx.core.recovery_manager import RecoveryManager
from jarvisx.core.task_manager import TaskManager
from jarvisx.agents.agent_monitor import AgentMonitor
from jarvisx.network.event_bus import DistributedEventBus
from jarvisx.core.distributed_scheduler import DistributedScheduler
from jarvisx.agents.capability_registry import CapabilityRegistry
from jarvisx.nodes.node_registry import NodeRegistry

from jarvisx.nodes.worker_node import WorkerNode

@pytest.mark.asyncio
async def test_recovery_manager():
    task_manager = TaskManager()
    agent_monitor = AgentMonitor()
    scheduler = DistributedScheduler(CapabilityRegistry(), NodeRegistry())
    bus = DistributedEventBus()
    
    # Need mock node in registry for scheduler to return it
    node2 = WorkerNode("node2", "TestNode2", {"cpu": 4})
    scheduler.node_registry.register_node(node2)
    # Register that agent1 is available on node2 in the agent monitor
    agent_monitor.register_heartbeat("agent1", "node2", True)
    
    rm = RecoveryManager(task_manager, agent_monitor, scheduler, bus)
    
    # Create a task on a failing node
    task_manager.create_task("job1", "node1", "agent1", "tr1")
    task_manager.update_status("job1", "RUNNING")
    
    # Simulate node crash
    await bus.publish("agent.connection.disconnected", {"node_id": "node1"})
    
    # Give the async handler time to run
    import asyncio
    await asyncio.sleep(0.1)
    
    # Recovery manager should have picked it up and migrated it
    task = task_manager.get_task("job1")
    assert task["status"] == "SUBMITTED" # Back to submitted state for redispatch
