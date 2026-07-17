"""Inter-Agent Message Bus — all agent communication routes through here via filesystem."""
import json
import os
import time
import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

MESSAGE_LOG_DIR = "var/message_bus"
HISTORY_DIR = os.path.join(MESSAGE_LOG_DIR, "history")


class MessageType(str, Enum):
    TASK_REQUEST = "TASK_REQUEST"
    TASK_RESULT = "TASK_RESULT"
    RESOURCE_REQUEST = "RESOURCE_REQUEST"
    RESOURCE_RELEASE = "RESOURCE_RELEASE"
    STATUS_UPDATE = "STATUS_UPDATE"
    ERROR_REPORT = "ERROR_REPORT"
    SHUTDOWN = "SHUTDOWN"


class Message:
    """A single message on the bus."""

    def __init__(
        self,
        sender_id: str,
        recipient_id: str,
        msg_type: MessageType,
        payload: Dict[str, Any],
        message_id: Optional[str] = None,
        timestamp: Optional[float] = None,
    ):
        self.message_id = message_id or f"msg_{uuid.uuid4().hex[:8]}"
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.msg_type = msg_type
        self.payload = payload
        self.timestamp = timestamp or time.time()
        self.acknowledged = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "msg_type": self.msg_type.value if isinstance(self.msg_type, Enum) else self.msg_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "acknowledged": self.acknowledged,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            msg_type=MessageType(data["msg_type"]),
            payload=data["payload"],
            message_id=data["message_id"],
            timestamp=data["timestamp"],
        )


class MessageBus:
    """File-system based message bus for true inter-process agent communication."""

    _instance: Optional["MessageBus"] = None

    def __init__(self):
        os.makedirs(HISTORY_DIR, exist_ok=True)

    @classmethod
    def get_instance(cls) -> "MessageBus":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    async def send(self, message: Message) -> None:
        """Write a message directly to the recipient's inbox folder."""
        recipient_dir = os.path.join(MESSAGE_LOG_DIR, message.recipient_id)
        os.makedirs(recipient_dir, exist_ok=True)
        
        filepath = os.path.join(recipient_dir, f"{message.message_id}.json")
        data = message.to_dict()
        
        # Write atomically
        temp_path = filepath + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, filepath)
        
        # Write to history
        history_path = os.path.join(HISTORY_DIR, f"{message.message_id}.json")
        with open(history_path, "w") as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Message {message.message_id} sent: {message.sender_id} -> {message.recipient_id} [{message.msg_type}]")

    async def receive(self, agent_id: str, timeout: float = 5.0) -> Optional[Message]:
        """Poll the recipient's inbox folder for new messages."""
        recipient_dir = os.path.join(MESSAGE_LOG_DIR, agent_id)
        os.makedirs(recipient_dir, exist_ok=True)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            files = [f for f in os.listdir(recipient_dir) if f.endswith(".json") and not f.endswith(".tmp")]
            if files:
                files.sort()  # Read oldest first
                filepath = os.path.join(recipient_dir, files[0])
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    os.remove(filepath)  # "Acknowledge" by deleting from inbox
                    msg = Message.from_dict(data)
                    msg.acknowledged = True
                    return msg
                except (json.JSONDecodeError, FileNotFoundError, PermissionError):
                    # File might be mid-write or just deleted
                    await asyncio.sleep(0.1)
                    continue
            await asyncio.sleep(0.1)
        return None

    def get_pending_count(self, agent_id: str) -> int:
        recipient_dir = os.path.join(MESSAGE_LOG_DIR, agent_id)
        if not os.path.exists(recipient_dir):
            return 0
        return len([f for f in os.listdir(recipient_dir) if f.endswith(".json") and not f.endswith(".tmp")])
