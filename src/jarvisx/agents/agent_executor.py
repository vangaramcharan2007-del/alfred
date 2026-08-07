"""Autonomous Agent Executor for Phase 91 Autonomous Mission Brain."""

from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from jarvisx.agents.action_models import ActionProposal, ExecutionResult, PolicyDecision
from jarvisx.agents.capability_registry import AutonomousCapabilityRegistry
from jarvisx.agents.execution_trace import ExecutionTraceRecorder
from jarvisx.agents.goal_decomposer import GoalDecomposer
from jarvisx.agents.mission_memory import MissionMemory
from jarvisx.agents.mission_state import MissionStateMachine, State
from jarvisx.agents.planner import StepPlanner
from jarvisx.agents.policy_engine import PolicyEngine
from jarvisx.agents.reflection_engine import ReflectionEngine


class AutonomousAgentExecutor:
    """Core autonomous ReAct execution loop engine."""

    def __init__(
        self,
        capability_registry: Optional[AutonomousCapabilityRegistry] = None,
        policy_engine: Optional[PolicyEngine] = None,
        memory: Optional[MissionMemory] = None,
    ):
        self.registry = capability_registry or AutonomousCapabilityRegistry()
        self.policy = policy_engine or PolicyEngine()
        self.memory = memory or MissionMemory()
        self.decomposer = GoalDecomposer()
        self.planner = StepPlanner(self.registry)
        self.reflection_engine = ReflectionEngine()

    def execute_mission(
        self,
        goal: str,
        base_dir: str = "var/missions",
        speak_fn: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Execute a complete autonomous mission from a single-sentence goal."""
        print(f"\n==================================================")
        print(f"  AUTONOMOUS MISSION BRAIN (PHASE 91)")
        print(f"==================================================")
        print(f"Goal: '{goal}'")

        # 1. State: CREATED -> PLANNING
        # Decompose Goal into Structured Milestones
        mission_info = self.decomposer.decompose(goal)
        mission_name = mission_info.get("mission_name", "custom_mission")
        mission_dir = Path(base_dir) / mission_name
        mission_dir.mkdir(parents=True, exist_ok=True)

        mission_state = MissionStateMachine(mission_id=mission_name, goal=goal)
        mission_state.transition_to(State.PLANNING, reason="Decomposing user goal into milestones")

        milestones = mission_info.get("milestones", [])
        total_milestones = len(milestones)

        # Save plan.json in mission directory
        plan_path = mission_dir / "plan.json"
        plan_path.write_text(json.dumps(mission_info, indent=2), encoding="utf-8")

        # Initialize Execution Trace Recorder
        trace_path = mission_dir / "execution_trace.json"
        trace_recorder = ExecutionTraceRecorder(str(trace_path))

        announce_msg = f"Mission created for '{mission_name}'. Analyzing {total_milestones} execution milestones..."
        print(f"\n[Mission Brain]: {announce_msg}")
        if speak_fn:
            speak_fn(announce_msg)

        # 2. State: PLANNING -> EXECUTING
        mission_state.transition_to(State.EXECUTING, reason="Starting capability action loop")

        completed_step_ids: List[str] = []
        successful_actions: List[str] = []
        failed_actions: List[str] = []
        artifacts_created: List[str] = [str(plan_path)]

        # 3. Autonomous Execution Loop (ReAct)
        max_loop_iterations = 10
        iteration = 0

        while len(completed_step_ids) < total_milestones and iteration < max_loop_iterations:
            iteration += 1

            # (A) Step Planner: Choose next action
            proposal: Optional[ActionProposal] = self.planner.get_next_action(
                mission_info=mission_info,
                completed_step_ids=completed_step_ids,
                mission_dir=str(mission_dir)
            )

            if not proposal:
                break

            print(f"\n[Step {proposal.step_index}/{total_milestones}]: {proposal.rationale}")

            # (B) Policy Validator: Safety & Risk Check
            cap = self.registry.get(proposal.capability_name)
            policy_check = self.policy.evaluate_proposal(proposal, cap)

            if policy_check["decision"] == PolicyDecision.BLOCK.value:
                print(f"[Policy Safety Gate]: Action BLOCKED: {policy_check['reason']}")
                failed_actions.append(f"{proposal.capability_name} (BLOCKED)")
                trace_recorder.record_step(
                    step_index=proposal.step_index,
                    action_name=proposal.capability_name,
                    tool="policy_gate",
                    parameters=proposal.arguments,
                    result_status="BLOCKED",
                    duration_sec=0.0,
                    artifacts=[],
                    notes=policy_check["reason"]
                )
                break

            # (C) Tool Execution
            start_t = time.time()
            try:
                raw_res = cap.handler(**proposal.arguments)
                duration = round(time.time() - start_t, 3)

                # Collect created artifacts
                created = []
                if isinstance(raw_res, dict):
                    for k in ("created_file", "document", "quiz_file"):
                        if k in raw_res and raw_res[k]:
                            created.append(str(raw_res[k]))
                            artifacts_created.append(str(raw_res[k]))

                exec_res = ExecutionResult(
                    action_name=proposal.capability_name,
                    status="SUCCESS",
                    output=raw_res,
                    duration_sec=duration,
                    artifacts_created=created
                )
                successful_actions.append(proposal.capability_name)
                # Match milestone ID
                m_id = f"m{proposal.step_index}"
                completed_step_ids.append(m_id)
                print(f"  [+] Success ({duration}s)")

            except Exception as e:
                duration = round(time.time() - start_t, 3)
                exec_res = ExecutionResult(
                    action_name=proposal.capability_name,
                    status="FAILED",
                    output=None,
                    duration_sec=duration,
                    error=str(e)
                )
                failed_actions.append(proposal.capability_name)
                print(f"  [-] Failed: {e}")

            # (D) Record Execution Trace
            trace_recorder.record_step(
                step_index=proposal.step_index,
                action_name=proposal.capability_name,
                tool=cap.name,
                parameters=proposal.arguments,
                result_status=exec_res.status,
                duration_sec=exec_res.duration_sec,
                artifacts=exec_res.artifacts_created,
                notes=proposal.expected_outcome
            )

            # (E) Reflection Engine: Observe & Reflect
            reflection = self.reflection_engine.evaluate(
                goal=goal,
                proposal=proposal,
                result=exec_res,
                total_milestones=total_milestones,
                completed_count=len(completed_step_ids)
            )

            if reflection.requires_replanning:
                mission_state.transition_to(State.REPLANNING, reason="Step failure triggered replan")
                mission_state.transition_to(State.EXECUTING, reason="Resuming execution")

        # 4. Final State Transition: COMPLETED or FAILED
        if len(completed_step_ids) >= total_milestones:
            mission_state.transition_to(State.COMPLETED, reason="All milestones verified")
            final_status = "SUCCESS"
        else:
            mission_state.transition_to(State.FAILED, reason="Incomplete milestones")
            final_status = "PARTIAL_FAILURE"

        # 5. Persist Mission Memory
        self.memory.save_mission(
            mission_id=mission_name,
            goal=goal,
            status=final_status,
            successful_actions=successful_actions,
            failed_actions=failed_actions,
            artifacts=artifacts_created,
            learned_context={"milestones_total": total_milestones, "milestones_completed": len(completed_step_ids)}
        )

        # 6. Final Voice Announcement & Summary Report
        summary_msg = f"Mission '{mission_name}' complete. All artifacts generated and verified on disk."
        print(f"\n[Mission Brain]: {summary_msg}\n")
        if speak_fn:
            speak_fn(summary_msg)

        return {
            "status": final_status,
            "mission_name": mission_name,
            "mission_dir": str(mission_dir),
            "total_milestones": total_milestones,
            "completed_milestones": len(completed_step_ids),
            "artifacts_created": artifacts_created,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "state_history": mission_state.history,
        }
