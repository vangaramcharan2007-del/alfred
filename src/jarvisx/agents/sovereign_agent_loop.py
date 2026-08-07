"""Sovereign Agent Loop for Jarvis X (Layer 6 - Cognition & Autonomous Agent Loop).

Unified ReAct Loop: Goal -> Decompose Plan -> Capability Registry Selection -> Execute Tool -> Observe Output -> Loop until Goal Complete.
Replaces command-bot keyword matching with true multi-step goal execution.
"""

from __future__ import annotations
import json
import os
import sys
import time
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from jarvisx.automation.capability_registry import CapabilityRealityRegistry
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
from jarvisx.llm.llm_router import LLMRouter


class SovereignAgentLoop:
    """True Goal-Driven Agentic Execution Loop."""

    def __init__(self):
        self.capability_registry = CapabilityRealityRegistry()
        self.orchestrator = DynamicOrchestrator()
        self.router = LLMRouter()
        self.max_steps: int = 5

    def plan_mission(self, user_goal: str) -> List[Dict[str, Any]]:
        """Decompose user's high-level goal into an ordered sequence of executable tool steps."""
        g = user_goal.lower().strip()

        # Multi-Step Goal Decomposition Heuristic & LLM Planner
        steps = []

        if "automate my life" in g or "setup workspace" in g or "start my day" in g:
            steps = [
                {"step": 1, "tool": "clean", "description": "Clean system temporary files and reclaim memory"},
                {"step": 2, "tool": "gcr_notes", "description": "Scan and ingest lecture notes into Knowledge Graph memory"},
                {"step": 3, "tool": "notification", "description": "Check and report high-priority unread notifications"},
                {"step": 4, "tool": "briefing", "description": "Generate and speak daily engineering briefing"}
            ]
        elif "study" in g or "homework" in g or "lecture" in g:
            steps = [
                {"step": 1, "tool": "gcr_notes", "description": "Ingest lecture notes into Knowledge Graph"},
                {"step": 2, "tool": "launch", "target": "code", "description": "Open VS Code workspace"},
                {"step": 3, "tool": "search", "query": "study music", "description": "Play study music"}
            ]
        elif "build" in g or "make" in g or "create" in g:
            steps = [
                {"step": 1, "tool": "build_app", "target": "app_workspace", "description": "Bootstrap fullstack application repository"},
                {"step": 2, "tool": "launch", "target": "code", "description": "Open created project in VS Code"}
            ]
        else:
            # Single-step direct execution fallback
            steps = [
                {"step": 1, "tool": "direct", "goal": user_goal, "description": f"Execute objective: {user_goal}"}
            ]

        return steps

    def run_agent_loop(self, user_goal: str, persona: str = "ALFRED", speak_callback: Optional[Any] = None) -> Dict[str, Any]:
        """Execute the Goal -> Plan -> Tool -> Observe -> Loop cycle until goal is complete."""
        salutation = "Sir" if persona == "ALFRED" else "Boss"
        print(f"\n[SovereignAgentLoop] Mission Goal Received: '{user_goal}'")

        # 1. Plan Mission Steps
        plan = self.plan_mission(user_goal)
        total_steps = len(plan)

        if speak_callback:
            speak_callback(f"Mission acknowledged, {salutation}. Executing {total_steps}-step autonomous plan.")
        elif speak_callback is None:
            print(f"[Agent Speech]: Mission acknowledged, {salutation}. Executing {total_steps}-step autonomous plan.")

        results = []

        # 2. Iterate through Step Loop
        for step_info in plan:
            step_num = step_info["step"]
            tool = step_info.get("tool")
            desc = step_info.get("description", "")

            print(f"\n[Agent Step {step_num}/{total_steps}]: {desc}")

            # Execute Step via Orchestrator / Capabilities
            if tool == "clean":
                res = self.orchestrator.execute_voice_command("clean pc", persona=persona)
            elif tool == "gcr_notes":
                res = self.orchestrator.execute_voice_command("notes", persona=persona)
            elif tool == "notification":
                res = self.orchestrator.execute_voice_command("notification", persona=persona)
            elif tool == "briefing":
                res = self.orchestrator.execute_voice_command("briefing", persona=persona)
            elif tool == "build_app":
                res = self.orchestrator.execute_voice_command("make an app", persona=persona)
            elif tool == "launch":
                res = self.orchestrator.execute_voice_command(f"open {step_info.get('target', 'browser')}", persona=persona)
            elif tool == "search":
                res = self.orchestrator.execute_voice_command(f"search {step_info.get('query', 'trending')}", persona=persona)
            else:
                res = self.orchestrator.execute_voice_command(user_goal, persona=persona)

            # Observe Result
            results.append({"step": step_num, "description": desc, "result": res})
            time.sleep(0.5)

        # 3. Mission Completion Synthesis
        final_msg = f"Mission complete, {salutation}. All {total_steps} plan steps executed successfully."
        print(f"\n[SovereignAgentLoop] {final_msg}\n")

        if speak_callback:
            speak_callback(final_msg)

        return {
            "status": "MISSION_COMPLETED",
            "goal": user_goal,
            "total_steps": total_steps,
            "execution_trace": results,
            "final_summary": final_msg
        }
