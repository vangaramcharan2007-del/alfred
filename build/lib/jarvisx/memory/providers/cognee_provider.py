import time
import uuid
from typing import Dict, Any, List, Optional
from jarvisx.core.logging import StructuredLogger
from jarvisx.memory.providers.memory_provider import MemoryProvider


class CogneeProvider(MemoryProvider):
    """
    Knowledge-graph-aware memory provider.
    Implements the MemoryProvider interface while maintaining an internal graph
    of entities and relationships. Drop-in replacement for SQLiteMemoryProvider.
    
    Architecture:
        CognitiveMemory → MemoryProvider Interface → CogneeProvider
        (Cognee is replaceable — swap in SQLite or Supabase without changing Alfred.)
    """

    def __init__(self, logger: Optional[StructuredLogger] = None) -> None:
        self.logger = logger or StructuredLogger()
        self._store: Dict[str, Dict[str, Any]] = {}
        self._graph_entities: Dict[str, Dict[str, Any]] = {}
        self._graph_relationships: List[Dict[str, Any]] = []

    # ─── MemoryProvider Interface ───────────────────────────────────────

    async def save(self, key: str, value: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> bool:
        self._store[key] = {
            "value": value,
            "context": context or {},
            "timestamp": time.time(),
        }
        return True

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()
        for k, v in self._store.items():
            value_str = str(v["value"]).lower()
            if query_lower in k.lower() or query_lower in value_str:
                results.append({"key": k, "data": v["value"], "meta": v["context"]})
        results.sort(key=lambda x: self._store[x["key"]]["timestamp"], reverse=True)
        return results[:limit]

    async def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    async def sync(self, node_id: str, diff: Dict[str, Any]) -> bool:
        for k, v in diff.items():
            await self.save(k, v, {"synced_from": node_id})
        return True

    # ─── Cognee-Specific Graph Methods ──────────────────────────────────

    def add_experience(self, experience: Dict[str, Any]) -> str:
        """Store a raw experience in the data store."""
        exp_id = f"exp_{uuid.uuid4().hex[:8]}"
        self._store[exp_id] = {
            "value": experience,
            "context": {"type": "experience"},
            "timestamp": time.time(),
        }
        return exp_id

    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Search the graph for entities matching a query."""
        results = []
        query_lower = query.lower()
        for entity in self._graph_entities.values():
            if query_lower in str(entity).lower():
                results.append(entity)
        return results

    def create_relationships(self, source: str, target: str, relation: str, confidence: float = 1.0) -> str:
        """Add a relationship to the internal graph."""
        rel_id = f"rel_{uuid.uuid4().hex[:8]}"
        self._graph_relationships.append({
            "id": rel_id,
            "source": source,
            "target": target,
            "relation": relation,
            "confidence": confidence,
        })
        return rel_id

    def retrieve_context(self, entity_id: str) -> Dict[str, Any]:
        """Retrieve an entity and its relationships from the graph."""
        entity = self._graph_entities.get(entity_id)
        rels = [r for r in self._graph_relationships if r["source"] == entity_id or r["target"] == entity_id]
        return {"entity": entity, "relationships": rels}

    def sync_graph(self, external_graph_data: Dict[str, Any]) -> bool:
        """Merge external graph data into the local graph."""
        if "entities" in external_graph_data:
            self._graph_entities.update(external_graph_data["entities"])
        if "relationships" in external_graph_data:
            self._graph_relationships.extend(external_graph_data["relationships"])
        return True
