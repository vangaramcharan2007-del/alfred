"""Alfred Master Coordinator for Phase 96 Multi-Agent Operating System."""

from __future__ import annotations
import time
import uuid
from typing import Dict, Any, List, Optional
from jarvisx.multi_agent.agent_bus import AgentCommunicationBus
from jarvisx.multi_agent.models import (
    AgentCapability,
    AgentMessage,
    AgentRole,
    MessageType,
    SubTask,
    TeamMissionResult,
)


class AlfredMasterCoordinator:
    """Master Multi-Agent Coordinator.
    Strictly coordinates and plans; delegates specialized subtasks to Researcher, Coder, and Friday.
    """

    def __init__(self, bus: AgentCommunicationBus):
        self.bus = bus
        self.capability = AgentCapability(
            name="AlfredMaster",
            role=AgentRole.COORDINATOR,
            skills=["goal_decomposition", "task_delegation", "result_synthesis"],
            permission_scope="coordination"
        )
        self.subtasks_in_flight: Dict[str, SubTask] = {}
        self.bus.subscribe("ALFRED", self.handle_agent_response)

    def handle_agent_response(self, message: AgentMessage) -> None:
        """Process results and status updates from specialized sub-agents."""
        task_id = message.payload.get("task_id")
        if task_id and task_id in self.subtasks_in_flight:
            subtask = self.subtasks_in_flight[task_id]
            if message.msg_type == MessageType.TASK_RESULT:
                subtask.status = "COMPLETED"
                subtask.result = message.payload.get("result")
            elif message.msg_type == MessageType.ERROR_REPORT:
                subtask.status = "FAILED"
                subtask.error = message.payload.get("error", "Agent error reported")

    def coordinate_mission(self, objective: str, project_name: Optional[str] = None) -> TeamMissionResult:
        """Decompose objective, delegate to specialists over bus, and synthesize final mission deliverable."""
        start_t = time.time()
        mission_id = f"tm_{str(uuid.uuid4())[:8]}"
        proj = project_name or objective.lower().replace(" ", "_")[:20]

        print(f"\n==================================================")
        print(f"  ALFRED MULTI-AGENT OS (PHASE 96)")
        print(f"==================================================")
        print(f"Objective: '{objective}'\n")

        # 1. Alfred Decomposes into Specialized Subtasks
        subtasks = [
            SubTask(
                id=f"{mission_id}_sub1",
                title=f"Research requirements & patterns for {objective}",
                agent_role=AgentRole.RESEARCHER,
                parameters={"topic": objective, "project_name": proj}
            ),
            SubTask(
                id=f"{mission_id}_sub2",
                title=f"Synthesize software application and test suite",
                agent_role=AgentRole.CODER,
                parameters={"project_name": proj, "objective": objective}
            ),
            SubTask(
                id=f"{mission_id}_sub3",
                title=f"Verify runtime artifacts on disk",
                agent_role=AgentRole.TACTICAL,
                parameters={"target_dir": f"var/missions/{proj}"}
            )
        ]

        for s in subtasks:
            self.subtasks_in_flight[s.id] = s

        # 2. Delegate Subtasks over Agent Communication Bus
        for s in subtasks:
            recipient_tag = s.agent_role.value
            print(f"[Alfred Coordinator]: Delegating '{s.title}' -> {recipient_tag}")
            self.bus.publish(AgentMessage(
                id=f"msg_{int(time.time()*1000)}",
                sender="ALFRED",
                recipient=recipient_tag,
                msg_type=MessageType.TASK_REQUEST,
                topic="EXECUTE_SUBTASK",
                payload={"task": s.to_dict()},
                timestamp=time.time()
            ))

        # 3. Synthesize Final Mission Deliverable
        duration = round(time.time() - start_t, 3)
        all_completed = all(s.status == "COMPLETED" for s in subtasks)
        status_str = "COMPLETED" if all_completed else "PARTIAL"

        artifacts = [
            f"var/missions/{proj}/app.py",
            f"var/missions/{proj}/test_app.py",
        ]

        print(f"\n[Alfred Coordinator]: Mission '{mission_id}' {status_str} in {duration}s. Team deliverables synthesized.\n")

        return TeamMissionResult(
            mission_id=mission_id,
            objective=objective,
            subtasks=subtasks,
            artifacts=artifacts,
            status=status_str,
            duration_sec=duration
        )
