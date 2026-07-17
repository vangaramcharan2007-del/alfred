"""Inter-Agent Message Bus — all agent communication routes through here."""
import json
import os
import time
import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

MESSAGE_LOG_DIR = "var/message_bus"


class MessageType(str, Enum):
    TASK_REQUEST = "TASK_REQUEST"
    TASK_RESULT = "TASK_RESULT"
    RESOURCE_REQUEST = "RESOURCE_REQUEST"
    RESOURCE_RELEASE = "RESOURCE_RELEASE"
    STATUS_UPDATE = "STATUS_UPDATE"
    ERROR_REPORT = "ERROR_REPORT"


class Message:
    """A single message on the bus."""

    def __init__(
        self,
        sender_id: str,
        recipient_id: str,
        msg_type: MessageType,
        payload: Dict[str, Any],
        message_id: Optional[str] = None,
    ):
        self.message_id = message_id or f"msg_{uuid.uuid4().hex[:8]}"
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.msg_type = msg_type
        self.payload = payload
        self.timestamp = time.time()
        self.acknowledged = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "msg_type": self.msg_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "acknowledged": self.acknowledged,
        }


class MessageBus:
    """Async message bus for inter-agent communication. All messages are persisted."""

    _instance: Optional["MessageBus"] = None

    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        self._history: List[Message] = []
        self._subscribers: Dict[str, List] = defaultdict(list)
        os.makedirs(MESSAGE_LOG_DIR, exist_ok=True)

    @classmethod
    def get_instance(cls) -> "MessageBus":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    async def send(self, message: Message) -> None:
        """Send a message to a recipient's queue and persist it."""
        self._history.append(message)
        await self._queues[message.recipient_id].put(message)
        self._persist_message(message)
        logger.info(
            f"Message {message.message_id}: {message.sender_id} -> {message.recipient_id} "
            f"[{message.msg_type.value}]"
        )

    async def receive(self, agent_id: str, timeout: float = 5.0) -> Optional[Message]:
        """Receive the next message for an agent, with timeout."""
        try:
            msg = await asyncio.wait_for(self._queues[agent_id].get(), timeout=timeout)
            msg.acknowledged = True
            return msg
        except asyncio.TimeoutError:
            return None

    def get_pending_count(self, agent_id: str) -> int:
        return self._queues[agent_id].qsize()

    def get_history(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if agent_id:
            return [
                m.to_dict() for m in self._history
                if m.sender_id == agent_id or m.recipient_id == agent_id
            ]
        return [m.to_dict() for m in self._history]

    def _persist_message(self, message: Message):
        filepath = os.path.join(MESSAGE_LOG_DIR, f"{message.message_id}.json")
        with open(filepath, "w") as f:
            json.dump(message.to_dict(), f, indent=2, default=str)
