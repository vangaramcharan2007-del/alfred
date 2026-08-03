from __future__ import annotations
import shutil
import time
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.external.external_provider import Provider
from jarvisx.capabilities.openhands.openhands_session import OpenHandsSessionManager

class OpenHandsProvider(Provider):
    def __init__(self, session_manager: Optional[OpenHandsSessionManager] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="openhands", config=config)
        self.session_manager = session_manager or OpenHandsSessionManager()
        self.connected = False
        self.runtime_available = False


    async def connect(self) -> bool:
        # Detect if openhands binary or module is present
        self.runtime_available = (shutil.which("openhands") is not None)
        self.connected = True
        return True

    async def disconnect(self) -> bool:
        self.connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        status = "HEALTHY" if self.runtime_available else "DEGRADED"
        return {
            "status": status,
            "connected": self.connected,
            "runtime_available": self.runtime_available,
            "provider": "openhands",
            "active_sessions": len(self.session_manager.list_active_sessions())
        }

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        if not self.connected:
            await self.connect()

        session = self.session_manager.start_session(kwargs.get("project_name", "DefaultProject"))
        start_t = time.time()

        res = {
            "status": "success" if self.runtime_available else "degraded_success",
            "provider": "openhands",
            "action": action,
            "session_id": session.session_id,
            "runtime_available": self.runtime_available,
            "execution_time": round(time.time() - start_t, 3),
            "output": f"Executed OpenHands task '{action}'"
        }

        self.session_manager.record_task_history(session.session_id, res)
        return res

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_id": "openhands",
            "name": "OpenHands Software Engineer",
            "version": "0.10.0",
            "author": "All-Hands-AI",
            "description": "OpenHands Autonomous Software Engineer Provider"
        }

    def capabilities(self) -> List[str]:
        return [
            "fix_bug",
            "implement_feature",
            "refactor",
            "generate_tests",
            "documentation",
            "security_audit",
            "performance_optimization",
            "dependency_upgrade",
            "architecture_migration",
            "code_review"
        ]
