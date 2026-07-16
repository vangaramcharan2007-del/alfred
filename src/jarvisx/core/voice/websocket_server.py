import asyncio
import json
import logging
from typing import Set

import websockets

logger = logging.getLogger(__name__)

class VoiceWebsocketServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8766):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self._server_task = None
        
        # State mapping
        self.current_state = "sleeping"
        self.active_personality = "Alfred"

    async def _handler(self, websocket, path):
        self.clients.add(websocket)
        try:
            # Send initial state
            await self.broadcast_state(self.current_state)
            # Wait for client to close
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)

    async def start(self):
        start_server = websockets.serve(self._handler, self.host, self.port)
        self._server = await start_server
        logger.info(f"Voice WebSocket server listening on ws://{self.host}:{self.port}")

    async def stop(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def broadcast_state(self, state: str):
        self.current_state = state
        message = json.dumps({
            "type": "state",
            "state": state,
            "personality": self.active_personality
        })
        await self._broadcast(message)

    async def broadcast_transcript(self, text: str, is_user: bool = False):
        message = json.dumps({
            "type": "transcript",
            "text": text,
            "is_user": is_user
        })
        await self._broadcast(message)

    async def _broadcast(self, message: str):
        if not self.clients:
            return
        # Create a copy of clients to avoid runtime changes
        for client in list(self.clients):
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                pass
