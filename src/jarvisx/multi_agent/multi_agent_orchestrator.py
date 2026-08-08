"""Multi-Agent Orchestrator wiring Alfred, Friday, Researcher, Coder, and Agent Bus."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.multi_agent.agent_bus import AgentCommunicationBus
from jarvisx.multi_agent.alfred_master import AlfredMasterCoordinator
from jarvisx.multi_agent.coding_agent import CodingAgent
from jarvisx.multi_agent.friday_tactical import FridayTacticalAgent
from jarvisx.multi_agent.research_agent import ResearchAgent
from jarvisx.multi_agent.models import TeamMissionResult


class MultiAgentOrchestrator:
    """Master Multi-Agent Runtime Orchestrator for Jarvis X (Phase 96)."""

    def __init__(self):
        self.bus = AgentCommunicationBus()
        self.researcher = ResearchAgent(self.bus)
        self.coder = CodingAgent(self.bus)
        self.friday = FridayTacticalAgent(self.bus)
        self.alfred = AlfredMasterCoordinator(self.bus)

    def run_team_mission(self, objective: str, project_name: Optional[str] = None) -> TeamMissionResult:
        """Execute a collaborative multi-agent mission with full role specialization."""
        return self.alfred.coordinate_mission(objective, project_name)

    def get_team_status(self) -> Dict[str, Any]:
        """Return status and capability matrix of all registered agents."""
        agents = [
            self.alfred.capability.to_dict(),
            self.researcher.capability.to_dict(),
            self.coder.capability.to_dict(),
            self.friday.capability.to_dict(),
        ]
        print(f"\n[MULTI-AGENT OS]: Registered Specialists ({len(agents)} active)")
        for a in agents:
            print(f"  • {a['name']} ({a['role']}) -> Scope: {a['permission_scope']} (Skills: {', '.join(a['skills'][:3])})")
        return {"agent_count": len(agents), "agents": agents}

    def explain_mission(self, mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return audit trail of all bus messages exchanged for team auditability."""
        messages = self.bus.get_messages(50)
        print(f"\n[MULTI-AGENT AUDIT]: Message Bus Telemetry ({len(messages)} messages)")
        logs = []
        for m in messages:
            print(f"  [{m.sender} -> {m.recipient}] {m.msg_type.value}: {m.topic}")
            logs.append(m.to_dict())
        return logs
