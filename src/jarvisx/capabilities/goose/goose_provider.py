from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.external.external_provider import Provider
from jarvisx.capabilities.goose.goose_session import GooseSessionManager
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.goose import goose_events as GE

class GooseProvider(Provider):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        bus: Optional[HermesBus] = None
    ):
        super().__init__(name="goose", config=config)
        self.bus = bus or HermesBus()
        self.session_mgr = GooseSessionManager()

    async def connect(self) -> bool:
        self.is_connected = True

        await self.bus.publish(Event(
            type=GE.GOOSE_CONNECTED,
            source="goose_provider",
            payload={"status": "connected", "runtime": "Goose Autonomous AI Engineer"}
        ))
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        for sess in self.session_mgr.list_active_sessions():
            self.session_mgr.terminate_session(sess.session_id)
            await self.bus.publish(Event(
                type=GE.GOOSE_SESSION_CLOSED,
                source="goose_provider",
                payload={"session_id": sess.session_id}
            ))
        return True

    async def health(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self.is_connected else "DISCONNECTED",
            "provider": "goose",
            "active_sessions": len(self.session_mgr.list_active_sessions())
        }

    async def execute(self, action: str, **kwargs) -> Any:
        if not self.is_connected:
            raise RuntimeError("Goose provider is not connected.")

        session_id = kwargs.get("session_id")
        session = self.session_mgr.get_session(session_id) if session_id else None
        if not session:
            session = self.session_mgr.create_session(kwargs.get("project_name", "JarvisXProject"))
            await self.bus.publish(Event(
                type=GE.GOOSE_SESSION_STARTED,
                source="goose_provider",
                payload={"session_id": session.session_id, "project": session.project_name}
            ))

        await self.bus.publish(Event(
            type=GE.GOOSE_TASK_STARTED,
            source="goose_provider",
            payload={"session_id": session.session_id, "action": action}
        ))

        # Perform action simulation / execution
        result = {
            "status": "success",
            "provider": "goose",
            "session_id": session.session_id,
            "action": action,
            "result": f"Goose executed engineering mission '{action}' with parameters {kwargs}"
        }

        self.session_mgr.record_task_history(session.session_id, {"action": action, "status": "success"})

        await self.bus.publish(Event(
            type=GE.GOOSE_TASK_COMPLETED,
            source="goose_provider",
            payload=result
        ))

        return result

    def capabilities(self) -> List[str]:
        return [
            "fix_bug",
            "implement_feature",
            "refactor_code",
            "generate_documentation",
            "improve_tests",
            "security_audit",
            "performance_optimization",
            "architecture_migration"
        ]

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Goose",
            "type": "autonomous_software_engineer",
            "version": "1.0.0",
            "runtime": "goose_engine"
        }
