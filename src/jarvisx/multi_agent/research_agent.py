"""Research & Knowledge Agent for Phase 96 Multi-Agent Operating System."""

from __future__ import annotations
import time
from typing import Dict, Any, Optional
from jarvisx.multi_agent.agent_bus import AgentCommunicationBus
from jarvisx.multi_agent.models import AgentCapability, AgentMessage, AgentRole, MessageType, SubTask


class ResearchAgent:
    """Specialized Knowledge & Research Agent.
    Strictly read-only; produces structured research reports and requirements definitions.
    """

    def __init__(self, bus: AgentCommunicationBus):
        self.bus = bus
        self.capability = AgentCapability(
            name="ResearchAgent",
            role=AgentRole.RESEARCHER,
            skills=["web_search", "academic_notes", "requirements_extraction", "doc_lookup"],
            permission_scope="read_only"
        )
        self.bus.subscribe("RESEARCHER", self.handle_task_request)

    def handle_task_request(self, message: AgentMessage) -> None:
        if message.msg_type == MessageType.TASK_REQUEST:
            task_dict = message.payload.get("task", {})
            subtask = SubTask(
                id=task_dict.get("id", "res_01"),
                title=task_dict.get("title", "Research Objective"),
                agent_role=AgentRole.RESEARCHER,
                parameters=task_dict.get("parameters", {})
            )
            result = self.execute_research(subtask)
            self.bus.publish(AgentMessage(
                id=f"res_out_{int(time.time()*1000)}",
                sender="RESEARCHER",
                recipient="ALFRED",
                msg_type=MessageType.TASK_RESULT,
                topic="RESEARCH_COMPLETED",
                payload={"task_id": subtask.id, "result": result},
                timestamp=time.time()
            ))

    def execute_research(self, task: SubTask) -> Dict[str, Any]:
        """Perform structured research and return structured research report."""
        topic = task.parameters.get("topic", task.title)
        print(f"  [Researcher Agent]: Analyzing requirements for '{topic}'...")

        report = {
            "type": "research_report",
            "topic": topic,
            "sections": {
                "Architecture": f"Modular design patterns for {topic}",
                "Key_Requirements": ["REST endpoints", "Data validation", "Test coverage >90%"],
                "Edge_Cases": ["Rate limiting", "Schema error handling", "Async latency"]
            },
            "recommended_technologies": ["FastAPI", "Pydantic", "Pytest", "Uvicorn"],
            "generated_at": time.time()
        }

        task.status = "COMPLETED"
        task.result = report
        return report
