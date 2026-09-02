from __future__ import annotations
import time
from typing import Dict, Any, Optional
from jarvisx.runtime.state import RuntimeState

class ShutdownManager:
    def __init__(self, state: RuntimeState):
        self.state = state

    async def graceful_shutdown(self) -> Dict[str, Any]:
        self.state.state_name = "SHUTTING_DOWN"
        for name, srv in self.state.services.items():
            srv.status = "OFFLINE"
            srv.updated_at = time.time()
        self.state.state_name = "STOPPED"
        return {
            "status": "STOPPED",
            "message": "Jarvis X runtime shutdown cleanly."
        }
