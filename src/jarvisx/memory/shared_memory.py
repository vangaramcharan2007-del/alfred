import json
from dataclasses import dataclass, field
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
from jarvisx.core.logging import StructuredLogger

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


from jarvisx.tools.base import BaseTool, ToolResult


class LocalMemoryTool(BaseTool):
    """Canonical offline-first JSONL persistent memory adapter."""
    name = "memory"

    def __init__(self, vault_path: Optional[str | Path] = None, logger: Optional[Any] = None):
        self.vault_path = Path(vault_path) if vault_path else Path("var/db/memory")
        self.file_path = self.vault_path / "memory.jsonl"
        self.logger = logger
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.file_path.exists():
                self.file_path.write_text("", encoding="utf-8")
        except Exception:
            pass

    def save_memory(self, text: str, category: str = "general", **kwargs: Any) -> ToolResult:
        try:
            record = {
                "id": f"rec_{time.time()}_{hash(text) % 10000}",
                "content": text,
                "category": category,
                "timestamp": time.time(),
            }
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            return ToolResult(success=True, message="Memory stored.", data={"record": record})
        except Exception as exc:
            return ToolResult(success=False, message=str(exc))

    def search_memory(self, query: str, limit: int = 10, **kwargs: Any) -> ToolResult:
        records: List[Dict[str, Any]] = []
        try:
            if self.file_path.exists():
                with open(self.file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            content = str(data.get("content", "")).lower()
                            words = [w.lower() for w in query.split() if len(w) > 2]
                            if not words or all(w in content for w in words) or query.lower() in content:
                                records.append(data)
                        except Exception:
                            continue
        except Exception as exc:
            return ToolResult(success=False, message=str(exc))
        return ToolResult(
            success=True,
            message=f"Found {len(records)} records.",
            data={"records": records[-limit:], "results": records[-limit:]},
        )
