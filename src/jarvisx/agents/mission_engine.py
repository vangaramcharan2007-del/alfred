"""Autonomous Mission Brain Top-Level Engine for Jarvis X (Phase 91)."""

from __future__ import annotations
import sys
from typing import Dict, Any, Optional, Callable
from jarvisx.agents.agent_executor import AutonomousAgentExecutor


class MissionBrainEngine:
    """The central nervous system for goal-driven autonomous mission execution."""

    def __init__(self):
        self.executor = AutonomousAgentExecutor()

    def execute_goal(self, goal: str, speak_fn: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """Accept any natural language goal and execute complete autonomous mission."""
        return self.executor.execute_mission(goal=goal, speak_fn=speak_fn)


def run_mission_cli(goal_str: str) -> None:
    """CLI runner for autonomous missions."""
    engine = MissionBrainEngine()
    res = engine.execute_goal(goal_str)
    print(f"\n[MISSION COMPLETE]: {res['status']}")
    print(f"Directory: {res['mission_dir']}")
    print(f"Artifacts: {len(res['artifacts_created'])}")
    for a in res["artifacts_created"]:
        print(f"  • {a}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_mission_cli(" ".join(sys.argv[1:]))
    else:
        run_mission_cli("Create a Python calculator project")
