from typing import Dict, Any, List, Optional
from jarvisx.core.logging import StructuredLogger
import time

class MemoryProvider:
    """Abstract interface for memory backends (SQLite, Cognee, Supabase)."""
    async def store(self, key: str, value: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        raise NotImplementedError
        
    async def retrieve(self, key: str) -> Optional[Any]:
        raise NotImplementedError
        
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError

class MockSQLiteProvider(MemoryProvider):
    """Simple in-memory local cache implementation for the shared memory phase."""
    def __init__(self):
        self._store = {}
        
    async def store(self, key: str, value: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        self._store[key] = {
            "value": value,
            "context": context or {},
            "timestamp": time.time()
        }
        return True
        
    async def retrieve(self, key: str) -> Optional[Any]:
        if key in self._store:
            return self._store[key]["value"]
        return None
        
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # Basic mock substring search
        results = []
        for k, v in self._store.items():
            if query.lower() in k.lower() or query.lower() in str(v["value"]).lower():
                results.append({"key": k, "data": v})
        return results[:limit]

class SharedMemory:
    """
    Centralized memory access allowing all nodes and agents to share knowledge.
    """
    def __init__(self, provider: MemoryProvider, logger: Optional[StructuredLogger] = None):
        self.provider = provider
        self.logger = logger or StructuredLogger()

    async def store_memory(self, key: str, value: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        success = await self.provider.store(key, value, context)
        if success:
            self.logger.write("info", "shared_memory.stored", key=key)
        return success

    async def retrieve_memory(self, key: str) -> Optional[Any]:
        self.logger.write("debug", "shared_memory.retrieve", key=key)
        return await self.provider.retrieve(key)

    async def sync_memory(self, node_id: str, diff: Dict[str, Any]) -> bool:
        """
        Synchronize memory diffs from a remote node into the shared global state.
        (Called via EventBus when a memory.updated event fires).
        """
        for k, v in diff.items():
            await self.store_memory(k, v, {"synced_from": node_id})
        self.logger.write("info", "shared_memory.synced", node=node_id, keys=list(diff.keys()))
        return True

    async def search_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        self.logger.write("info", "shared_memory.search", query=query)
        return await self.provider.search(query, limit)
