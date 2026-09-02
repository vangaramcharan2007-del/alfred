from __future__ import annotations
import time
from typing import Dict, Any, List, Optional

class ContextManager:
    def __init__(self):
        self.context_stack: List[Dict[str, Any]] = []

    def push_context(self, user_request: str, intent: Dict[str, Any], route: Dict[str, Any]) -> Dict[str, Any]:
        ctx = {
            "request": user_request,
            "intent": intent,
            "route": route,
            "timestamp": time.time()
        }
        self.context_stack.append(ctx)
        return ctx

    def current_context(self) -> Optional[Dict[str, Any]]:
        return self.context_stack[-1] if self.context_stack else None

    def history(self) -> List[Dict[str, Any]]:
        return list(self.context_stack)
