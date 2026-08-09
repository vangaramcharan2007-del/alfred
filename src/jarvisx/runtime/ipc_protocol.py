"""IPC Protocol Definition & Message Serialization for Phase 104."""

from __future__ import annotations
import json
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class IPCMessageType(str, Enum):
    PING = "PING"
    EXECUTE_COMMAND = "EXECUTE_COMMAND"
    GET_STATUS = "GET_STATUS"
    TRIGGER_EVENT = "TRIGGER_EVENT"
    GET_BRIEFING = "GET_BRIEFING"
    SHUTDOWN = "SHUTDOWN"
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"


@dataclass
class IPCMessage:
    msg_type: IPCMessageType
    payload: Dict[str, Any] = field(default_factory=dict)
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: str = "OK"  # OK, ERROR, REJECTED
    error: Optional[str] = None

    def serialize(self) -> bytes:
        """Encode message to newline-terminated UTF-8 JSON bytes."""
        data = {
            "msg_id": self.msg_id,
            "msg_type": self.msg_type.value,
            "payload": self.payload,
            "status": self.status,
            "error": self.error,
        }
        return (json.dumps(data) + "\n").encode("utf-8")

    @classmethod
    def deserialize(cls, data_bytes: bytes) -> IPCMessage:
        """Decode newline-terminated UTF-8 JSON bytes to IPCMessage."""
        text = data_bytes.decode("utf-8").strip()
        data = json.loads(text)
        return cls(
            msg_id=data.get("msg_id", ""),
            msg_type=IPCMessageType(data.get("msg_type", "PING")),
            payload=data.get("payload", {}),
            status=data.get("status", "OK"),
            error=data.get("error"),
        )
