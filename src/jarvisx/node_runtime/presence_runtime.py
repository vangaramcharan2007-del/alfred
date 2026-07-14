import asyncio
import logging
import time

logger = logging.getLogger("PresenceRuntime")

class PresenceRuntime:
    def __init__(self):
        self.active_nodes = {}
        self.running = False
        self.task = None

    async def start_heartbeat(self):
        self.running = True
        self.task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Presence service started. Heartbeats active.")

    async def stop_heartbeat(self):
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Presence service stopped.")

    async def _heartbeat_loop(self):
        while self.running:
            self._register_heartbeat("node-001-primary")
            self._evict_stale_nodes()
            await asyncio.sleep(5)

    def _register_heartbeat(self, node_id: str):
        self.active_nodes[node_id] = time.time()
    
    def _evict_stale_nodes(self):
        now = time.time()
        stale = [node for node, last_seen in self.active_nodes.items() if now - last_seen > 15]
        for node in stale:
            del self.active_nodes[node]
            logger.warning(f"Node {node} evicted due to timeout.")
