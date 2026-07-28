import asyncio
import time
from typing import Dict, Any, Optional

from jarvisx.network.agent_protocol import Envelope, TransportInterface
from jarvisx.core.logging import StructuredLogger

class MockTransport(TransportInterface):
    """
    Simulated transport layer using asyncio queues for testing the distributed mesh locally.
    Designed so a future WebSocket implementation can replace this seamlessly.
    """
    def __init__(self):
        # Maps node_id to a tuple of (tx_queue, rx_queue)
        # where tx_queue is for messages sent TO the node, rx is for messages RECEIVED FROM the node.
        self.queues: Dict[str, tuple[asyncio.Queue, asyncio.Queue]] = {}
        
    def register_queues(self, node_id: str, tx: asyncio.Queue, rx: asyncio.Queue):
        self.queues[node_id] = (tx, rx)

    async def send_message(self, node_id: str, message: Envelope) -> None:
        if node_id in self.queues:
            tx, _ = self.queues[node_id]
            await tx.put(message)

    async def receive_message(self, node_id: str) -> Optional[Envelope]:
        if node_id in self.queues:
            _, rx = self.queues[node_id]
            return await rx.get()
        return None

    async def broadcast(self, message: Envelope) -> None:
        for node_id, (tx, _) in self.queues.items():
            await tx.put(message)


class AgentGateway:
    """
    Maintains real-time connections with remote worker nodes.
    Responsible for tracking connection state, handling reconnects, and message passing.
    """
    def __init__(self, transport: TransportInterface, logger: Optional[StructuredLogger] = None):
        self.transport = transport
        self.logger = logger or StructuredLogger()
        self._connections: Dict[str, Dict[str, Any]] = {}

    async def connect_node(self, node_id: str, connection_id: str) -> None:
        """Establish a new connection with a remote node."""
        self._connections[node_id] = {
            "node_id": node_id,
            "connection_id": connection_id,
            "status": "connected",
            "last_seen": time.time(),
            "latency": 0
        }
        self.logger.write("info", "gateway.node_connected", node=node_id, connection=connection_id)

    async def disconnect_node(self, node_id: str) -> None:
        """Close an active connection."""
        if node_id in self._connections:
            self._connections[node_id]["status"] = "disconnected"
            self.logger.write("info", "gateway.node_disconnected", node=node_id)

    def get_connection_status(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve connection telemetry."""
        return self._connections.get(node_id)

    async def send_message(self, node_id: str, message: Envelope) -> None:
        """Push a message through the transport layer to the node."""
        if node_id in self._connections and self._connections[node_id]["status"] == "connected":
            await self.transport.send_message(node_id, message)
            self._connections[node_id]["last_seen"] = time.time()
        else:
            self.logger.write("warning", "gateway.send_failed_offline", node=node_id)

    async def receive_message(self, node_id: str) -> Optional[Envelope]:
        """Pull a message from the transport layer."""
        if node_id in self._connections and self._connections[node_id]["status"] == "connected":
            msg = await self.transport.receive_message(node_id)
            if msg:
                self._connections[node_id]["last_seen"] = time.time()
                return msg
        return None

    async def broadcast(self, message: Envelope) -> None:
        """Broadcast a message to all connected nodes."""
        await self.transport.broadcast(message)
        now = time.time()
        for node in self._connections.values():
            if node["status"] == "connected":
                node["last_seen"] = now
