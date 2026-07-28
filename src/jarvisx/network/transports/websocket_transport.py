import asyncio
import time
from typing import Dict, Optional, Any
from jarvisx.network.agent_protocol import Envelope, TransportInterface
from jarvisx.core.logging import StructuredLogger
from jarvisx.network.event_bus import DistributedEventBus

class WebSocketTransport(TransportInterface):
    """
    Dependency-free async stub that simulates a real WebSocket transport layer.
    Manages connection state, reconnects, heartbeats, and message routing.
    """
    def __init__(self, logger: Optional[StructuredLogger] = None, event_bus: Optional[DistributedEventBus] = None):
        self.logger = logger or StructuredLogger()
        self.event_bus = event_bus
        # Track simulated connections
        self.connections: Dict[str, Dict[str, Any]] = {}
        # Message queues for simulating network transit per node
        self.tx_queues: Dict[str, asyncio.Queue] = {}
        self.rx_queues: Dict[str, asyncio.Queue] = {}

    async def connect(self, node_id: str, connection_id: str) -> None:
        """Establish a simulated WebSocket connection."""
        self.connections[node_id] = {
            "node_id": node_id,
            "connection_id": connection_id,
            "status": "connected",
            "last_seen": time.time(),
            "latency": 50 # simulated latency in ms
        }
        if node_id not in self.tx_queues:
            self.tx_queues[node_id] = asyncio.Queue()
            self.rx_queues[node_id] = asyncio.Queue()
            
        self.logger.write("info", "websocket.connected", node_id=node_id, connection_id=connection_id)
        if self.event_bus:
            await self.event_bus.publish("agent.connection.connected", self.connections[node_id])

    async def disconnect(self, node_id: str) -> None:
        """Close the WebSocket connection."""
        if node_id in self.connections:
            self.connections[node_id]["status"] = "disconnected"
            self.logger.write("info", "websocket.disconnected", node_id=node_id)
            if self.event_bus:
                await self.event_bus.publish("agent.connection.disconnected", self.connections[node_id])

    async def send(self, node_id: str, message: Envelope) -> None:
        """Send a message over the WebSocket."""
        conn = self.connections.get(node_id)
        if conn and conn["status"] == "connected":
            # Simulate network delay
            await asyncio.sleep(conn["latency"] / 1000.0)
            await self.rx_queues[node_id].put(message) # Put in RX so receive() can get it
            conn["last_seen"] = time.time()
        else:
            self.logger.write("warning", "websocket.send_failed", node_id=node_id, reason="Not connected")

    async def receive(self, node_id: str) -> Optional[Envelope]:
        """Receive a message from the WebSocket."""
        conn = self.connections.get(node_id)
        if conn and conn["status"] == "connected":
            msg = await self.rx_queues[node_id].get()
            conn["last_seen"] = time.time()
            return msg
        return None

    async def heartbeat(self, node_id: str) -> None:
        """Simulate a ping/pong heartbeat."""
        conn = self.connections.get(node_id)
        if conn and conn["status"] == "connected":
            conn["last_seen"] = time.time()
            self.logger.write("debug", "websocket.heartbeat", node_id=node_id)

    async def reconnect(self, node_id: str) -> None:
        """Attempt to reconnect a disconnected socket."""
        conn = self.connections.get(node_id)
        if conn:
            conn["status"] = "reconnecting"
            self.logger.write("info", "websocket.reconnecting", node_id=node_id)
            if self.event_bus:
                await self.event_bus.publish("agent.connection.reconnecting", conn)
                
            await asyncio.sleep(0.5) # Simulate connection delay
            conn["status"] = "connected"
            conn["last_seen"] = time.time()
            self.logger.write("info", "websocket.reconnected", node_id=node_id)
            if self.event_bus:
                await self.event_bus.publish("agent.connection.connected", conn)

    # Implement TransportInterface abstractions
    async def send_message(self, node_id: str, message: Envelope) -> None:
        await self.send(node_id, message)

    async def receive_message(self, node_id: str) -> Optional[Envelope]:
        return await self.receive(node_id)

    async def broadcast(self, message: Envelope) -> None:
        for node_id in self.connections.keys():
            await self.send(node_id, message)
