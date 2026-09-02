from __future__ import annotations
from typing import Dict, Any, List

class ToolTrace:
    """
    Records tool invocations and output responses.
    """
    def __init__(self):
        self.invocations: List[Dict[str, Any]] = []

    def record_invocation(self, tool_id: str, status: str, output_snippet: str):
        self.invocations.append({
            "tool_id": tool_id,
            "status": status,
            "snippet": output_snippet[:200]
        })
