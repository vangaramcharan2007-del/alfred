import logging
import asyncio

logger = logging.getLogger("InitiativeDaemon")

class InitiativeDaemon:
    """
    Continuously evaluates the WorldModelRuntime against predefined opportunity triggers
    and dispatches autonomous background tasks.
    """
    def __init__(self, world_model, scheduler, executor, transport):
        self.world_model = world_model
        self.scheduler = scheduler
        self.executor = executor
        self.transport = transport
        self.running = False

    async def start(self):
        self.running = True
        logger.info("Initiative Daemon started background observation loop.")
        asyncio.create_task(self._observation_loop())

    async def stop(self):
        self.running = False
        logger.info("Initiative Daemon stopped.")

    async def _observation_loop(self):
        while self.running:
            state = self.world_model.get_snapshot()
            
            # Check for low battery trigger
            for node_id, metrics in state.get("devices", {}).items():
                if metrics.get("battery_percent", 100) < 20 and metrics.get("is_executing_heavy_task", False):
                    logger.warning(f"InitiativeTrigger: Node {node_id} battery critical while executing heavy task.")
                    await self._take_autonomous_action(node_id)
            
            await asyncio.sleep(2)

    async def _take_autonomous_action(self, struggling_node_id: str):
        logger.info(f"Autonomously resolving issue for {struggling_node_id}...")
        
        # Determine best fallback node
        best_node = self.scheduler.determine_best_node({"cpu_intensive": True})
        
        if best_node != struggling_node_id:
            logger.info(f"InitiativeAction: Migrating workload from {struggling_node_id} to {best_node}")
            # Dispatch command over mesh
            await self.transport.broadcast_message({
                "type": "MIGRATE_TASK",
                "target_node": best_node,
                "source_node": struggling_node_id,
                "task_id": "heavy-compute-999"
            })
            # Assume success for simulation purposes
            self.world_model.state["devices"][struggling_node_id]["is_executing_heavy_task"] = False
        else:
            logger.warning("InitiativeAction: No suitable fallback node available.")
