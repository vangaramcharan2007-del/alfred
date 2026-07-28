from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class TaskRequest:
    task_id: str
    trace_id: str
    agent_id: str
    required_capabilities: List[str]
    payload: Dict[str, Any]
    priority: int = 5
    deadline: Optional[float] = None

@dataclass
class TaskResponse:
    task_id: str
    trace_id: str
    status: str
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

class AgentProtocol:
    """
    Abstract base class for remote agent communication protocols.
    Future implementations: WebSocketAgentProtocol, gRPCAgentProtocol, RESTAgentProtocol.
    """
    
    async def dispatch_task(self, node_id: str, request: TaskRequest) -> str:
        """
        Dispatches a task to a remote node.
        Returns a job_id for tracking progress asynchronously.
        """
        raise NotImplementedError
        
    async def poll_status(self, job_id: str) -> TaskResponse:
        """
        Polls the status of a remote job.
        """
        raise NotImplementedError
