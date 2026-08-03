from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

@dataclass
class SystemNode:
    entity_id: str
    entity_type: str  # capability, provider, model, agent, tool, repository, memory
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "name": self.name,
            "metadata": self.metadata
        }

@dataclass
class SystemEdge:
    source_id: str
    target_id: str
    relation: str  # uses, depends_on, improves, replaces, conflicts_with

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation
        }

class SystemKnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, SystemNode] = {}
        self.edges: List[SystemEdge] = []

    def add_node(self, entity_id: str, entity_type: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> SystemNode:
        node = SystemNode(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            metadata=metadata or {}
        )
        self.nodes[entity_id] = node
        return node

    def add_edge(self, source_id: str, target_id: str, relation: str) -> SystemEdge:
        edge = SystemEdge(source_id=source_id, target_id=target_id, relation=relation)
        self.edges.append(edge)
        return edge

    def query_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        rel = []
        for e in self.edges:
            if e.source_id == entity_id or e.target_id == entity_id:
                rel.append(e.to_dict())
        return rel

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes_count": len(self.nodes),
            "edges_count": len(self.edges),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }
