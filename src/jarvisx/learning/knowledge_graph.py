import uuid
from typing import Dict, Any, List, Optional
from jarvisx.core.logging import StructuredLogger


class KnowledgeGraph:
    """
    Maintains relationships between concepts as a lightweight in-memory graph.
    Supports entity/relationship CRUD and traversal queries.
    """

    def __init__(self, logger: Optional[StructuredLogger] = None) -> None:
        self._entities: Dict[str, Dict[str, Any]] = {}
        self._relationships: List[Dict[str, Any]] = []
        self.logger = logger or StructuredLogger()

    def add_entity(self, name: str, entity_type: str, attributes: Optional[Dict[str, Any]] = None) -> str:
        """Add an entity node. Returns entity ID."""
        # Deduplicate by name
        existing = self.get_entity(name)
        if existing:
            return existing["id"]

        entity_id = f"ent_{uuid.uuid4().hex[:8]}"
        self._entities[entity_id] = {
            "id": entity_id,
            "name": name,
            "type": entity_type,
            "attributes": attributes or {},
        }
        self.logger.write("debug", "graph.entity_added", name=name, entity_type=entity_type)
        return entity_id

    def add_relationship(self, source: str, target: str, relation: str, confidence: float = 1.0) -> str:
        """Add a relationship edge. Returns relationship ID."""
        # Deduplicate: don't add the same relationship twice
        for rel in self._relationships:
            if rel["source"] == source and rel["target"] == target and rel["relation"] == relation:
                # Update confidence if higher
                if confidence > rel["confidence"]:
                    rel["confidence"] = confidence
                return rel["id"]

        rel_id = f"rel_{uuid.uuid4().hex[:8]}"
        self._relationships.append({
            "id": rel_id,
            "source": source,
            "target": target,
            "relation": relation,
            "confidence": confidence,
        })
        self.logger.write("debug", "graph.relationship_added", source=source, target=target, relation=relation)
        return rel_id

    def query_relationships(self, entity_name: str) -> List[Dict[str, Any]]:
        """Find all relationships involving an entity (by name)."""
        return [r for r in self._relationships if r["source"] == entity_name or r["target"] == entity_name]

    def find_related(self, entity_name: str, relation_type: Optional[str] = None) -> List[str]:
        """Find related entity names, optionally filtered by relation type."""
        related: set[str] = set()
        for rel in self._relationships:
            if relation_type and rel["relation"] != relation_type:
                continue
            if rel["source"] == entity_name:
                related.add(rel["target"])
            elif rel["target"] == entity_name:
                related.add(rel["source"])
        return sorted(related)

    def get_entity(self, name: str) -> Optional[Dict[str, Any]]:
        """Get entity by name."""
        for entity in self._entities.values():
            if entity["name"] == name:
                return entity
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the entire graph."""
        return {
            "entities": dict(self._entities),
            "relationships": list(self._relationships),
            "entity_count": len(self._entities),
            "relationship_count": len(self._relationships),
        }
