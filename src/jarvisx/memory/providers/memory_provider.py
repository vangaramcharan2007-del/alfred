from typing import Dict, Any, List, Optional

class MemoryProvider:
    """
    Abstract interface for cognitive memory backends.
    Implementations must handle the persistence and retrieval of structured memory.
    """
    async def save(self, key: str, value: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> bool:
        """Store or update a memory record."""
        raise NotImplementedError
        
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory records."""
        raise NotImplementedError
        
    async def delete(self, key: str) -> bool:
        """Remove a memory record."""
        raise NotImplementedError
        
    async def sync(self, node_id: str, diff: Dict[str, Any]) -> bool:
        """Synchronize memory with remote nodes."""
        raise NotImplementedError
