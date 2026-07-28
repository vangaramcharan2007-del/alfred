import time
from typing import Dict, Any, List, Optional
from jarvisx.memory.providers.memory_provider import MemoryProvider

class SQLiteMemoryProvider(MemoryProvider):
    """
    Local persistent memory backend for Cognitive Memory.
    For this milestone, implemented as a mock dictionary to simulate SQLite/persistence behavior
    without requiring external database setup.
    """
    def __init__(self):
        # In a real implementation, this would connect to an SQLite file.
        self._store: Dict[str, Dict[str, Any]] = {}
        
    async def save(self, key: str, value: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> bool:
        self._store[key] = {
            "value": value,
            "context": context or {},
            "timestamp": time.time()
        }
        return True
        
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        for k, v in self._store.items():
            value_str = str(v["value"]).lower()
            if query.lower() in k.lower() or query.lower() in value_str:
                results.append({"key": k, "data": v["value"], "meta": v["context"]})
        
        # Sort by timestamp desc
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
