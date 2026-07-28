from typing import Optional, Dict, Any
import asyncio
from jarvisx.core.task_manager import TaskManager
from jarvisx.agents.agent_monitor import AgentMonitor
from jarvisx.network.event_bus import DistributedEventBus
from jarvisx.core.logging import StructuredLogger
from jarvisx.core.distributed_scheduler import DistributedScheduler

class RecoveryManager:
    """
    Monitors the mesh for failures and automatically recovers or migrates tasks.
    """
    def __init__(
        self,
        task_manager: TaskManager,
        agent_monitor: AgentMonitor,
        scheduler: DistributedScheduler,
        event_bus: DistributedEventBus,
        logger: Optional[StructuredLogger] = None
    ):
        self.task_manager = task_manager
        self.agent_monitor = agent_monitor
        self.scheduler = scheduler
        self.event_bus = event_bus
        self.logger = logger or StructuredLogger()
        
        # Subscribe to failure events
        self.event_bus.subscribe("agent.connection.disconnected", self.detect_failure)
        self.event_bus.subscribe("task.failed", self.detect_failure)
        self.event_bus.subscribe("agent.crashed", self.detect_failure)

    async def detect_failure(self, event_payload: Dict[str, Any]) -> None:
        """Handle failure events dynamically from the event bus."""
        node_id = event_payload.get("node_id") or event_payload.get("node")
        task_id = event_payload.get("task_id")
        
        self.logger.write("warning", "recovery.failure_detected", node=node_id, task=task_id)
        
        if node_id:
            # Node went offline, we need to recover all running tasks on this node
            active_tasks = self.task_manager.list_active_tasks()
            for task in active_tasks:
                if task.get("node") == node_id and task["status"] in ["RUNNING", "SUBMITTED"]:
                    await self.recover_task(task["task_id"], task)
        elif task_id:
            # A specific task failed
            task = self.task_manager.get_task(task_id)
            if task:
                await self.recover_task(task_id, task)

    async def recover_task(self, task_id: str, task_context: Dict[str, Any]) -> None:
        """Attempt to recover a failed task by re-assigning it to a healthy node."""
        self.logger.write("info", "recovery.task_recovery_initiated", task=task_id)
        
        # In a real system, we might check retry counts here
        await self.migrate_task(task_id, task_context)

    async def migrate_task(self, task_id: str, task_context: Dict[str, Any]) -> None:
        """Migrate a task to a new healthy node using the scheduler."""
        # Find a new node for the required agent
        agent_id = task_context.get("agent")
        if not agent_id:
            self.logger.write("error", "recovery.migrate_failed_no_agent", task=task_id)
            return

        # Use scheduler to find a healthy node
        selected_node = self.scheduler.select_best_node(
            agent_id=agent_id,
            required_capabilities=[], # ideally preserved in task_context
            nodes_telemetry=self.agent_monitor.list_health()
        )
        
        if selected_node:
            self.logger.write("info", "recovery.task_migrated", task=task_id, new_node=selected_node)
            # Re-queue the task with the new node
            self.task_manager.update_status(task_id, "SUBMITTED", node=selected_node)
            # In a fully integrated system, the Gateway/Alfred would dispatch this again.
        else:
            self.logger.write("error", "recovery.migrate_failed_no_nodes", task=task_id)
            self.task_manager.update_status(task_id, "FAILED")

    async def restart_agent(self, agent_id: str, node_id: str) -> None:
        """Signal a node to restart a crashed agent process."""
        self.logger.write("info", "recovery.restart_agent_signaled", agent=agent_id, node=node_id)
        # Would send a control message via the gateway to the node runtime
        await self.event_bus.publish("system.control.restart_agent", {"agent_id": agent_id, "node_id": node_id})
