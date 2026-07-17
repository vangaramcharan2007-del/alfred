"""Agent Worker — the standalone process loop for an autonomous agent."""
import os
import json
import time
import asyncio
import logging
from typing import Optional

from jarvisx.core.agents.message_bus import MessageBus, Message, MessageType
from jarvisx.core.tools.tool_registry import ToolRegistry

HEARTBEAT_DIR = "var/heartbeats"


class AgentWorker:
    """A standalone event loop for a specific agent identity."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.bus = MessageBus.get_instance()
        self.tool_registry = ToolRegistry.get_instance()
        
        # Configure logging to write to {agent_id}.log
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # File handler
        fh = logging.FileHandler(f"{agent_id}.log", mode='w')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        # Also log to console
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    async def _send_heartbeat(self):
        """Continuously writes heartbeat JSON."""
        os.makedirs(HEARTBEAT_DIR, exist_ok=True)
        heartbeat_path = os.path.join(HEARTBEAT_DIR, f"{self.agent_id}.json")
        
        while True:
            data = {
                "agent_id": self.agent_id,
                "pid": os.getpid(),
                "last_seen": time.time(),
                "status": "RUNNING"
            }
            temp_path = heartbeat_path + ".tmp"
            try:
                with open(temp_path, "w") as f:
                    json.dump(data, f)
                os.replace(temp_path, heartbeat_path)
            except Exception as e:
                self.logger.error(f"Failed to write heartbeat: {e}")
            await asyncio.sleep(1.0)

    async def _process_messages(self):
        """Continuously polls the message bus for new tasks."""
        self.logger.info(f"{self.agent_id} starting message loop (PID: {os.getpid()})")
        while True:
            msg = await self.bus.receive(self.agent_id, timeout=1.0)
            if msg and msg.msg_type == MessageType.TASK_REQUEST:
                await self._handle_task(msg)

    async def _handle_task(self, msg: Message):
        self.logger.info(f"Received TASK_REQUEST from {msg.sender_id} for objective: {msg.payload.get('objective_id')}")
        
        objective_id = msg.payload.get("objective_id")
        tool_name = msg.payload.get("tool")
        method_name = msg.payload.get("method")
        args = msg.payload.get("args", {})
        
        # Execute tool
        self.logger.info(f"Executing tool {tool_name}.{method_name}")
        result = await self.tool_registry.execute(tool_name, method_name, args)
        
        # Send result back
        self.logger.info(f"Sending TASK_RESULT to {msg.sender_id}")
        await self.bus.send(Message(
            sender_id=self.agent_id,
            recipient_id=msg.sender_id,
            msg_type=MessageType.TASK_RESULT,
            payload={
                "objective_id": objective_id,
                "success": result.get("success", False),
                "error": result.get("error"),
                "evidence": result.get("evidence", {})
            }
        ))

    async def run(self):
        """Run the agent worker loop."""
        # Create heartbeat directory if needed
        os.makedirs(HEARTBEAT_DIR, exist_ok=True)
        
        heartbeat_task = asyncio.create_task(self._send_heartbeat())
        process_task = asyncio.create_task(self._process_messages())
        
        try:
            await asyncio.gather(heartbeat_task, process_task)
        except asyncio.CancelledError:
            self.logger.info("Worker cancelled, shutting down.")


def run_agent_worker(agent_id: str):
    """Entry point for multiprocessing."""
    worker = AgentWorker(agent_id)
    try:
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        worker.logger.info("Worker interrupted by user.")
