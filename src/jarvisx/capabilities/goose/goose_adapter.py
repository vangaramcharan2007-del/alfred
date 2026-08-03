from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.core.hermes import HermesBus
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.goose.goose_provider import GooseProvider
from jarvisx.capabilities.goose.goose_executor import GooseExecutor
from jarvisx.capabilities.coding.architecture_agent import ArchitectureAgent
from jarvisx.capabilities.coding.pipeline.task_planner import TaskPlanner
from jarvisx.capabilities.coding.pipeline.repository_analyzer import RepositoryAnalyzer
from jarvisx.capabilities.coding.code_graph import CodeGraph
from jarvisx.capabilities.coding.change_risk import ChangeRiskAnalyzer
from jarvisx.capabilities.github.github_capability import GitHubCapability

class GooseCapabilityAdapter:
    def __init__(
        self,
        bus: Optional[HermesBus] = None,
        provider: Optional[GooseProvider] = None,
        arch_agent: Optional[ArchitectureAgent] = None,
        github_cap: Optional[GitHubCapability] = None
    ):
        self.bus = bus or HermesBus()
        self.provider = provider or GooseProvider(bus=self.bus)
        self.arch_agent = arch_agent or ArchitectureAgent(bus=self.bus)
        self.github_cap = github_cap or GitHubCapability(bus=self.bus)

        self.executor = GooseExecutor(bus=self.bus)
        self.task_planner = TaskPlanner()
        self.repo_analyzer = RepositoryAnalyzer()
        self.code_graph = CodeGraph()
        self.risk_analyzer = ChangeRiskAnalyzer()

    def get_descriptor(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            id="goose.engineering",
            name="Goose Autonomous Engineering Runtime",
            version="1.0.0",
            author="Jarvis X / Goose Runtime",
            category="coding",
            permissions=["READ", "WRITE", "EXECUTE"],
            supported_actions=self.provider.capabilities(),
            handler=self.execute_action
        )

    async def register(self, registry: CapabilityRegistry) -> None:
        if not self.provider.is_connected:
            await self.provider.connect()
        descriptor = self.get_descriptor()
        await registry.register(descriptor)

    async def execute_action(self, action: str, **kwargs) -> Any:
        # Pre-execution pipeline integration: Architecture & Risk Audit
        repo_path = kwargs.get("repo_path", ".")
        idea = kwargs.get("task_description", f"Mission: {action}")

        # 1. Repository Analysis & CodeGraph
        repo_profile = self.repo_analyzer.generate_profile(repo_path)
        self.code_graph.build_from_repository(repo_path)

        # 2. Architecture Plan
        arch_proposal = await self.arch_agent.design_system(idea)

        # 3. Mission Execution via GooseExecutor & Provider
        session_id = kwargs.get("session_id", "default_sess")
        res = await self.executor.execute_mission(
            mission_type=action,
            task_description=idea,
            repo_path=repo_path,
            session_id=session_id,
            params=kwargs
        )

        return {
            "status": "success",
            "mission": res,
            "architecture_plan": arch_proposal["project_name"],
            "repository_profile": repo_profile.to_dict()
        }
