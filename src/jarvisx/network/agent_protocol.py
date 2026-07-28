from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import json

@dataclass
class Envelope:
    """Message envelope for all agent protocol communications."""
    message_id: str
    trace_id: str
    timestamp: str
    type: str
    payload: Dict[str, Any]
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))
        
    @staticmethod
    def from_json(data: str) -> "Envelope":
        parsed = json.loads(data)
        return Envelope(**parsed)

@dataclass
class TaskRequest:
    task_id: str
    trace_id: str
    agent_id: str
    required_capabilities: List[str]
    payload: Dict[str, Any]
    priority: int = 5
    deadline: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TaskAccepted:
    task_id: str
    node_id: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TaskProgress:
    task_id: str
    progress: int
    message: str
    current_stage: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TaskCompleted:
    task_id: str
    status: str
    result: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TaskFailed:
    task_id: str
    error: str
    recoverable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class TransportInterface:
    """Abstract interface for async message transport."""
    async def send_message(self, node_id: str, message: Envelope) -> None:
        raise NotImplementedError
        
    async def receive_message(self, node_id: str) -> Optional[Envelope]:
        raise NotImplementedError
        
    async def broadcast(self, message: Envelope) -> None:
        raise NotImplementedError
