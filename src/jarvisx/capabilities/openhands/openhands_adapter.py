from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.openhands.openhands_provider import OpenHandsProvider
from jarvisx.capabilities.openhands.openhands_workspace import OpenHandsWorkspaceManager
from jarvisx.capabilities.openhands.openhands_session import OpenHandsSessionManager
from jarvisx.capabilities.openhands.openhands_executor import OpenHandsExecutor
from jarvisx.capabilities.coding.pipeline.repository_analyzer import RepositoryAnalyzer
from jarvisx.capabilities.coding.code_graph import CodeGraph
from jarvisx.capabilities.coding.architecture_agent import ArchitectureAgent
from jarvisx.capabilities.coding.change_risk import ChangeRiskAnalyzer
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
import jarvisx.capabilities.openhands.openhands_events as OE

from jarvisx.capabilities.coding.pipeline.code_executor import FileChangeRecord

class OpenHandsCapabilityAdapter:

    def __init__(
        self,
        provider: Optional[OpenHandsProvider] = None,
        workspace_manager: Optional[OpenHandsWorkspaceManager] = None,
        session_manager: Optional[OpenHandsSessionManager] = None,
        executor: Optional[OpenHandsExecutor] = None,
        bus: Optional[HermesBus] = None
    ):
        self.session_manager = session_manager or OpenHandsSessionManager()
        self.workspace_manager = workspace_manager or OpenHandsWorkspaceManager()
        self.provider = provider or OpenHandsProvider(session_manager=self.session_manager)
        self.executor = executor or OpenHandsExecutor(bus=bus)
        self.bus = bus or HermesBus()

        self.repo_analyzer = RepositoryAnalyzer()
        self.code_graph = CodeGraph()
        self.arch_agent = ArchitectureAgent()
        self.risk_analyzer = ChangeRiskAnalyzer()

    def get_descriptors(self) -> List[CapabilityDescriptor]:
        return [
            CapabilityDescriptor(
                id="openhands.engineering",
                name="OpenHands Engineering Engine",
                version="1.0.0",
                author="Jarvis X",
                category="engineering",
                supported_actions=[
                    "fix_bug", "implement_feature", "refactor", "generate_tests",
                    "documentation", "security_audit", "performance_optimization",
                    "dependency_upgrade", "architecture_migration", "code_review"
                ],
                handler=self.execute_engineering_action
            ),
            CapabilityDescriptor(
                id="openhands.workspace",
                name="OpenHands Workspace Manager",
                version="1.0.0",
                author="Jarvis X",
                category="workspace",
                supported_actions=["create_workspace", "open_repository", "close_workspace", "reset_workspace"],
                handler=self.execute_workspace_action
            ),
            CapabilityDescriptor(
                id="openhands.review",
                name="OpenHands Code Reviewer",
                version="1.0.0",
                author="Jarvis X",
                category="review",
                supported_actions=["review_code", "assess_risk"],
                handler=self.execute_review_action
            ),
            CapabilityDescriptor(
                id="openhands.execution",
                name="OpenHands Task Execution",
                version="1.0.0",
                author="Jarvis X",
                category="execution",
                supported_actions=["run_mission", "stream_progress"],
                handler=self.execute_execution_action
            )
        ]

    async def register(self, registry: CapabilityRegistry) -> None:
        await self.provider.connect()
        await self.bus.publish(Event(
            type=OE.OPENHANDS_CONNECTED,
            source="openhands_adapter",
            payload={"status": "connected", "runtime_available": self.provider.runtime_available}
        ))

        for desc in self.get_descriptors():
            await registry.register(desc)

    async def execute_engineering_action(self, action: str, **kwargs) -> Dict[str, Any]:
        task_desc = kwargs.get("task_description", f"OpenHands engineering task: {action}")
        repo_path = kwargs.get("repo_path", "./")
        session_id = kwargs.get("session_id", "oh_sess_default")

        # Workspace setup
        ws = self.workspace_manager.open_repository(repo_path)
        await self.bus.publish(Event(
            type=OE.OPENHANDS_WORKSPACE_CREATED,
            source="openhands_adapter",
            payload={"workspace_id": ws.workspace_id, "path": ws.path}
        ))

        # 1. Pre-execution Code Analysis
        profile = self.repo_analyzer.generate_profile(repo_path)


        # 2. Pre-execution Architecture Plan
        arch_plan = await self.arch_agent.design_system(task_desc)
        arch_name = arch_plan.get("project_name", "OpenHandsSystem")


        # 3. Mission Execution
        res = await self.executor.execute_mission(
            mission_type=action,
            task_description=task_desc,
            repo_path=repo_path,
            session_id=session_id,
            params=kwargs
        )

        return {
            "status": "success",
            "provider": "openhands",
            "action": action,
            "repository_profile": profile.to_dict(),
            "architecture_plan": arch_name,

            "mission": res,
            "workspace": ws.to_dict()
        }

    async def execute_workspace_action(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "create_workspace":
            ws = self.workspace_manager.create_workspace(kwargs.get("path"), kwargs.get("persistent", True))
            return {"workspace": ws.to_dict()}
        elif action == "open_repository":
            ws = self.workspace_manager.open_repository(kwargs.get("repo_path", "./"))
            return {"workspace": ws.to_dict()}
        elif action == "close_workspace":
            ok = self.workspace_manager.close_workspace(kwargs.get("workspace_id", ""))
            return {"success": ok}
        elif action == "reset_workspace":
            ok = self.workspace_manager.reset_workspace(kwargs.get("workspace_id", ""))
            return {"success": ok}

        raise NotImplementedError(f"Workspace action '{action}' is not supported.")

    async def execute_review_action(self, action: str, **kwargs) -> Dict[str, Any]:
        raw_changes = kwargs.get("file_changes", [])
        records = [
            FileChangeRecord(
                file_path=c.get("file_path", "unknown"),
                action=c.get("action", "modified"),
                content_after=c.get("content_after", "")
            ) if isinstance(c, dict) else c
            for c in raw_changes
        ]
        risk = self.risk_analyzer.calculate_risk(records)
        return {"action": action, "risk_assessment": risk.to_dict()}


    async def execute_execution_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return {"action": action, "status": "executed", "provider": "openhands"}
