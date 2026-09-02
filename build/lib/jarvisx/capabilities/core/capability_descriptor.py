from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Awaitable

@dataclass
class CapabilityDescriptor:
    id: str
    name: str
    version: str = "1.0.0"
    author: str = "Jarvis X"
    category: str = "core"  # "coding", "mcp", "external", "tools", "robotics"
    permissions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    health_status: str = "HEALTHY"  # "HEALTHY", "DEGRADED", "UNHEALTHY", "UNLOADED"
    metrics: Dict[str, Any] = field(default_factory=dict)
    supported_actions: List[str] = field(default_factory=list)
    handler: Optional[Callable[..., Awaitable[Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "category": self.category,
            "permissions": self.permissions,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "metrics": self.metrics,
            "supported_actions": self.supported_actions
        }
