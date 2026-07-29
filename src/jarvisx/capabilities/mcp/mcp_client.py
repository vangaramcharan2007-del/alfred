from __future__ import annotations
from typing import Dict, Any

class MCPClient:
    async def connect(self) -> None:
        pass
    
    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"mcp_response": "called"}
    
    async def close(self) -> None:
        pass
