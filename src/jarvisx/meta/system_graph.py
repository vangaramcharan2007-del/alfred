from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

@dataclass
class SystemNode:
    entity_id: str
    entity_type: str  # capability, agent, model, repository, memory, mission, failure, improvement, evolution_history
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
    relation: str  # uses, depends_on, improves, replaces, conflicts_with, executes, records

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

    # First-class entity tracking helpers
    def add_capability(self, entity_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> SystemNode:
        return self.add_node(entity_id, "capability", name, metadata)

    def add_agent(self, entity_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> SystemNode:
        return self.add_node(entity_id, "agent", name, metadata)

    def add_model(self, entity_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> SystemNode:
        return self.add_node(entity_id, "model", name, metadata)

    def add_repository(self, entity_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> SystemNode:
        return self.add_node(entity_id, "repository", name, metadata)

    def add_memory(self, entity_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> SystemNode:
        return self.add_node(entity_id, "memory", name, metadata)

    def add_mission(self, entity_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> SystemNode:
        return self.add_node(entity_id, "mission", name, metadata)

    def add_failure(self, entity_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> SystemNode:
        return self.add_node(entity_id, "failure", name, metadata)

    def add_improvement(self, entity_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> SystemNode:
        return self.add_node(entity_id, "improvement", name, metadata)

    def add_evolution_history(self, entity_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> SystemNode:
        return self.add_node(entity_id, "evolution_history", name, metadata)

    def get_nodes_by_type(self, entity_type: str) -> List[SystemNode]:
        return [n for n in self.nodes.values() if n.entity_type == entity_type]

    def query_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        rel = []
        for e in self.edges:
            if e.source_id == entity_id or e.target_id == entity_id:
                rel.append(e.to_dict())
        return rel

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for n in self.nodes.values():
            counts[n.entity_type] = counts.get(n.entity_type, 0) + 1
        return counts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes_count": len(self.nodes),
            "edges_count": len(self.edges),
            "type_summary": self.summary(),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }

