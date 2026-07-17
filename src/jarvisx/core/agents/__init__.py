"""Agent __init__ — exports all multi-agent coordination components."""
from .agent_identity import AgentIdentity, AgentState
from .agent_registry import AgentRegistry
from .message_bus import MessageBus, Message, MessageType
from .shared_context import SharedContext
from .resource_manager import ResourceManager
from .agent_metrics import AgentMetrics
from .agent_coordinator import AgentCoordinator, SubObjective

__all__ = [
    "AgentIdentity",
    "AgentState",
    "AgentRegistry",
    "MessageBus",
    "Message",
    "MessageType",
    "SharedContext",
    "ResourceManager",
    "AgentMetrics",
    "AgentCoordinator",
    "SubObjective",
]
