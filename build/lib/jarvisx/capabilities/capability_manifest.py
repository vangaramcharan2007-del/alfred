from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class CapabilityContract:
    id: str
    name: str
    version: str
    description: str
    permissions_required: List[str] = field(default_factory=list)
    available_actions: List[str] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)
    health_status: Dict[str, Any] = field(default_factory=dict)
    initialization_method: str = "initialize"
    category: str = ""
    api_version: str = ""
    requirements: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "permissions_required": list(self.permissions_required),
            "available_actions": list(self.available_actions),
            "available_tools": list(self.available_tools),
            "health_status": dict(self.health_status),
            "initialization_method": self.initialization_method,
            "category": self.category,
            "api_version": self.api_version,
            "requirements": dict(self.requirements),
        }

@dataclass
class CapabilityManifest:
    name: str
    version: str
    api_version: str
    description: str
    category: str
    id: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    confidence: float = 1.0

    @property
    def capability_id(self) -> str:
        return self.id or self.name

    @property
    def available_actions(self) -> List[str]:
        return list(self.actions)

    @property
    def available_tools(self) -> List[str]:
        return list(self.tools)

    def to_contract(
        self,
        *,
        health_status: Optional[Dict[str, Any]] = None,
        initialization_method: str = "initialize",
    ) -> CapabilityContract:
        return CapabilityContract(
            id=self.capability_id,
            name=self.name,
            version=self.version,
            description=self.description,
            permissions_required=list(self.permissions),
            available_actions=self.available_actions,
            available_tools=self.available_tools,
            health_status=health_status or {},
            initialization_method=initialization_method,
            category=self.category,
            api_version=self.api_version,
            requirements=dict(self.requirements),
        )
