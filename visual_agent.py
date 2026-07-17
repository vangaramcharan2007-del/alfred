"""Visual Agent Worker for Phase 11 Demonstration."""
import os
import sys
import time
import json
import asyncio
import logging
from typing import Dict, Any

from jarvisx.core.agents.agent_identity import AgentIdentity
from jarvisx.core.agents.agent_worker import AgentWorker
from jarvisx.core.agents.message_bus import MessageBus, Message, MessageType
from jarvisx.core.agents.resource_manager import ResourceManager
from jarvisx.core.tools.tool_registry import ToolRegistry

class DemoTool:
    def __init__(self, name: str, sleep_time: float = 2.0):
        self.name = name
        self.sleep_time = sleep_time
        
    def do_work(self, action: str, resource: str):
        time.sleep(self.sleep_time)
        if action == "delete_all" and "mock_downloads" in resource:
            import os
            import shutil
            if os.path.exists(resource):
                for f in os.listdir(resource):
                    file_path = os.path.join(resource, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        return {"success": True, "evidence": {"action": action, "resource": resource}}

class VisualAgentWorker(AgentWorker):
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.messages_sent = 0
        self.messages_received = 0
        self.active_task = "None"
        self.resource_manager = ResourceManager.get_instance()
        
        # Suppress standard logging to console so it doesn't mess up the UI
        self.logger.propagate = False
        self.logger.handlers = []
        
        # File handler only
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(f"{agent_id}.log", mode='w')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    async def _handle_task(self, msg: Message):
        self.messages_received += 1
        objective_id = msg.payload.get("objective_id")
        self.active_task = f"Executing {objective_id}"
        
        await super()._handle_task(msg)
        
        self.messages_sent += 1
        self.active_task = "None"
        
    async def _process_messages(self):
        self.logger.info(f"{self.agent_id} starting message loop (PID: {os.getpid()})")
        while True:
            msg = await self.bus.receive(self.agent_id, timeout=1.0)
            if msg:
                if msg.msg_type == MessageType.TASK_REQUEST:
                    await self._handle_task(msg)
                elif msg.msg_type.name == "SHUTDOWN" or getattr(msg, 'msg_type') == "SHUTDOWN" or (isinstance(msg.msg_type, str) and msg.msg_type == "SHUTDOWN"):
                    # Custom shutdown logic
                    self.active_task = "SHUTTING DOWN (waiting 30s)"
                    await asyncio.sleep(30.0)
                    sys.exit(0)

    async def ui_loop(self):
        """Displays a live dashboard for this specific agent."""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"==================================================")
            print(f" AGENT: {self.agent_id.upper()}")
            print(f"==================================================")
            print(f" PID              : {os.getpid()}")
            print(f" Active Task      : {self.active_task}")
            
            # Lock status
            locked_resources = self.resource_manager.get_locked_resources()
            my_locks = [res for res, owner in locked_resources.items() if owner == self.agent_id]
            locks_str = ", ".join(my_locks) if my_locks else "None"
            print(f" Lock Status      : {locks_str}")
            
            # Heartbeat age
            heartbeat_age = "Unknown"
            heartbeat_file = os.path.join("var", "heartbeats", f"{self.agent_id}.json")
            if os.path.exists(heartbeat_file):
                try:
                    with open(heartbeat_file, "r") as f:
                        hb = json.load(f)
                        age = time.time() - hb["last_seen"]
                        heartbeat_age = f"{age:.1f}s ago"
                except Exception:
                    pass
            print(f" Heartbeat Age    : {heartbeat_age}")
            
            print(f" Messages Sent    : {self.messages_sent}")
            print(f" Messages Received: {self.messages_received}")
            print(f"==================================================")
            print("Logs are being written to file. Monitoring...")
            
            await asyncio.sleep(0.5)

    async def run(self):
        os.makedirs("var/heartbeats", exist_ok=True)
        heartbeat_task = asyncio.create_task(self._send_heartbeat())
        process_task = asyncio.create_task(self._process_messages())
        ui_task = asyncio.create_task(self.ui_loop())
        
        try:
            await asyncio.gather(heartbeat_task, process_task, ui_task)
        except asyncio.CancelledError:
            self.logger.info("Worker cancelled, shutting down.")


def main():
    if len(sys.argv) < 4:
        print("Usage: python visual_agent.py <agent_id> <tool_name> <sleep_time>")
        sys.exit(1)
        
    agent_id = sys.argv[1]
    tool_name = sys.argv[2]
    sleep_time = float(sys.argv[3])
    
    # Register the tool
    registry = ToolRegistry.get_instance()
    registry.register(DemoTool(tool_name, sleep_time), tool_name)
    
    worker = VisualAgentWorker(agent_id)
    try:
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
