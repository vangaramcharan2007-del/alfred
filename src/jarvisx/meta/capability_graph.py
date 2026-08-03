from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

@dataclass
class CapabilityNode:
    id: str
    name: str
    category: str
    actions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "actions": self.actions,
            "dependencies": self.dependencies
        }

class CapabilityGraph:
    def __init__(self):
        self.nodes: Dict[str, CapabilityNode] = {}
        self.edges: Dict[str, Set[str]] = {}  # node_id -> set of dependency node_ids

    def add_capability(self, node: CapabilityNode) -> None:
        self.nodes[node.id] = node
        if node.id not in self.edges:
            self.edges[node.id] = set()
        for dep in node.dependencies:
            self.edges[node.id].add(dep)

    def get_capability(self, capability_id: str) -> Optional[CapabilityNode]:
        return self.nodes.get(capability_id)

    def get_dependencies(self, capability_id: str) -> List[str]:
        return list(self.edges.get(capability_id, set()))

    def get_missing_dependencies(self, capability_id: str) -> List[str]:
        deps = self.get_dependencies(capability_id)
        return [dep for dep in deps if dep not in self.nodes]

    def list_nodes(self) -> List[CapabilityNode]:
        return list(self.nodes.values())
