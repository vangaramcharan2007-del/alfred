"""Alfred Personal OS Kernel for Jarvis X.

Unifies study organization, engineering automation, background project monitoring,
and autonomous workforce dispatch into a centralized executive controller in Layer 2.
"""

from typing import Any, Dict, List, Optional
import uuid

from jarvisx.agents import (
    AgentRegistry,
    CodingAgent,
    DevOpsAgent,
    GuardianAgent,
    ProductivityAgent,
    ResearchAgent,
    TestingAgent,
)
from jarvisx.automation import DevelopmentWorkflow, ProjectGuardian
from jarvisx.productivity import PersonalKnowledgeBase, StudyScheduler
from jarvisx.runtime import MissionRuntime


class PersonalOSKernel:
    """Unified executive controller for study workflows, engineering loops, and project health."""

    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        runtime: Optional[MissionRuntime] = None,
        dev_workflow: Optional[DevelopmentWorkflow] = None,
        productivity_agent: Optional[ProductivityAgent] = None,
        guardian_agent: Optional[GuardianAgent] = None,
        devops_agent: Optional[DevOpsAgent] = None,
    ):
        self.id = str(uuid.uuid4())
        self.registry = registry or self._init_workforce()
        self.runtime = runtime or MissionRuntime()
        self.dev_workflow = dev_workflow or DevelopmentWorkflow(registry=self.registry)

        self.productivity_agent = (
            productivity_agent
            or (self.registry.get_agent("productivity_agent") if self.registry.get_agent("productivity_agent") else None)
            or ProductivityAgent()
        )
        self.guardian_agent = (
            guardian_agent
            or (self.registry.get_agent("guardian_agent") if self.registry.get_agent("guardian_agent") else None)
            or GuardianAgent()
        )
        self.devops_agent = (
            devops_agent
            or (self.registry.get_agent("devops_agent") if self.registry.get_agent("devops_agent") else None)
            or DevOpsAgent()
        )

        self.execution_log: List[Dict[str, Any]] = []
        self._kernel_hspw: float = 0.0

    def _init_workforce(self) -> AgentRegistry:
        reg = AgentRegistry()
        reg.register(ResearchAgent())
        reg.register(TestingAgent())
        reg.register(CodingAgent())
        reg.register(ProductivityAgent())
        reg.register(GuardianAgent())
        reg.register(DevOpsAgent())
        return reg

    def execute_objective(self, request: str, **kwargs: Any) -> Dict[str, Any]:
        """Classify and route user instructions across academic, engineering, DevOps, or diagnostic handlers."""
        req_lower = request.lower()
        res: Dict[str, Any] = {}

        if any(w in req_lower for w in ["study", "revision", "exam", "note", "assignment", "college"]):
            action = kwargs.get("action", "schedule_revision" if "revision" in req_lower else "add_assignment")
            payload = {"action": action, "course": kwargs.get("course", "General Study"), **kwargs}
            if isinstance(self.productivity_agent, ProductivityAgent):
                res = self.productivity_agent.execute(payload)
            else:
                res = {"status": "error", "error": "Productivity worker unavailable"}
            self._kernel_hspw += 0.5

        elif any(w in req_lower for w in ["pr", "pull request", "triage", "issue", "release", "devops", "deploy"]):
            action = kwargs.get("action", "pr_create" if any(k in req_lower for k in ["pr", "pull request"]) else ("triage" if "issue" in req_lower else "release"))
            payload = {"action": action, **kwargs}
            if isinstance(self.devops_agent, DevOpsAgent):
                res = self.devops_agent.execute(payload)
            else:
                res = {"status": "error", "error": "DevOps worker unavailable"}
            self._kernel_hspw += 0.8

        elif any(w in req_lower for w in ["health", "audit", "sweep", "monitor", "clean", "regression"]):
            payload = {"action": "sweep", "target_dir": kwargs.get("target_dir", ".")}
            if isinstance(self.guardian_agent, GuardianAgent):
                res = self.guardian_agent.execute(payload)
            else:
                res = {"status": "error", "error": "Guardian worker unavailable"}
            self._kernel_hspw += 0.3

        elif any(w in req_lower for w in ["develop", "code", "feature", "build", "refactor", "implement"]):
            target_file = kwargs.get("target_file", "src/feature.py")
            sample_code = kwargs.get("sample_code", f"def {request.lower().split()[0]}():\n    return True\n")
            res = self.dev_workflow.run_loop(objective=request, target_file=target_file, sample_code=sample_code)
            self._kernel_hspw += 1.5

        else:
            mission = self.runtime.create_mission(goal=request)
            mission.add_task("Deconstruct objective and delegate to operational workers", handler="research_agent")
            mission.add_task("Synthesize findings into execution deliverable", handler="coding_agent")
            res = self.runtime.execute(mission)
            self._kernel_hspw += 1.0

        record = {"objective": request, "outcome": res.get("status", "unknown"), "summary": res}
        self.execution_log.append(record)
        return res

    def get_master_dashboard(self) -> Dict[str, Any]:
        """Synthesize consolidated master control report and total cumulative HSPW across all layers."""
        workforce_health = self.registry.health()
        guardian_stat = self.guardian_agent.execute({"action": "report"}) if isinstance(self.guardian_agent, GuardianAgent) else {"output": "Offline"}
        study_stat = self.productivity_agent.execute({"action": "dashboard"}) if isinstance(self.productivity_agent, ProductivityAgent) else {"output": "Offline"}
        devops_stat = self.devops_agent.execute({"action": "status"}) if isinstance(self.devops_agent, DevOpsAgent) else {"output": "Offline"}

        total_hspw = (
            workforce_health.get("total_hours_saved", 0.0)
            + self._kernel_hspw
            + (2.5 if self.execution_log else 0.0)
        )

        lines = [
            "=================================================================",
            "              ALFRED PERSONAL OS MASTER DASHBOARD                ",
            "=================================================================",
            f"Workforce Status: {workforce_health.get('workforce_status', 'NOMINAL')} ({workforce_health.get('active_healthy', 0)}/{workforce_health.get('total_workers', 0)} agents active)",
            f"Total Cumulative Time Saved: +{total_hspw:.2f} HSPW",
            f"Active Objectives Executed: {len(self.execution_log)} missions logged",
            "-----------------------------------------------------------------",
            "[SYSTEM HYGIENE & PROJECT GUARDIAN]",
            f"{guardian_stat.get('output', 'Status nominal').strip()}",
            "-----------------------------------------------------------------",
            "[PERSONAL PRODUCTIVITY & ACADEMICS]",
            f"{study_stat.get('output', 'Status nominal').strip()}",
            "-----------------------------------------------------------------",
            "[DEVOPS & RELEASE ENGINEERING]",
            f"{devops_stat.get('output', 'Status nominal').strip()}",
            "-----------------------------------------------------------------",
            "[ENGINEERING & WORKFLOW AUTOMATION]",
            f"Current Development Stage: {self.dev_workflow.current_stage.value}",
            f"Drafted Modifications: {len(self.dev_workflow.code_modifications)} staged packages",
            "=================================================================",
        ]

        return {
            "status": "nominal",
            "workforce_health": workforce_health,
            "total_hspw": total_hspw,
            "objectives_count": len(self.execution_log),
            "output": "\n".join(lines),
        }
