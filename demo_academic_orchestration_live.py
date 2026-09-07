"""Live Demonstration: Jarvis X Master Fleet & Meta-Orchestrator Academic Integration.

Demonstrates:
1. Fleet Registration: Dynamic discovery of AcademicSentinelAgent and HomeworkAgent.
2. Capability discovery: Academic Sentinel skills and permissions.
3. Unified Agent Fleet async task dispatch.
4. Meta-Orchestrator requirement analysis and dynamic routing.
5. Live end-to-end execution of an academic mission through the orchestrator.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Ensure project root and src are on path
project_root = Path(__file__).resolve().parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from jarvisx.orchestration.unified_agent_fleet import UnifiedAgentFleet
from jarvisx.orchestration.meta_orchestrator import MetaOrchestrator
from jarvisx.agents.registry import AgentRegistry


def print_banner(text: str):
    line = "=" * 70
    print(f"\n{line}")
    print(f"  {text}")
    print(f"{line}\n")


async def run_live_fleet_demonstration():
    print_banner("JARVIS X MASTER FLEET — ACADEMIC ORCHESTRATION DEMO")
    start_time = time.time()

    # Step 1: Initialize Fleet
    print("[1/5] Booting Unified Agent Fleet...")
    fleet = UnifiedAgentFleet.get_instance()
    fleet_agents = fleet.list_agents()
    print(f"      Fleet loaded with {len(fleet_agents)} active agents.")

    academic_agent = fleet.get_agent("AcademicSentinelAgent")
    homework_agent = fleet.get_agent("HomeworkAgent")
    assert academic_agent is not None, "AcademicSentinelAgent failed to load in fleet!"
    assert homework_agent is not None, "HomeworkAgent alias failed to load in fleet!"
    print(f"      [OK] AcademicSentinelAgent: ONLINE")
    print(f"      [OK] HomeworkAgent Alias: ONLINE")
    print(f"      Capabilities: {academic_agent.capabilities[:4]}...")

    # Step 2: Agent Telemetry via Fleet Dispatch
    print("\n[2/5] Dispatching status query via UnifiedAgentFleet.dispatch_task_async()...")
    status_result = await fleet.dispatch_task_async("AcademicSentinelAgent", {"action": "status"})
    res_data = status_result.get("result", {})
    print(f"      Student: {res_data.get('student')} (Reg: {res_data.get('reg_no')})")
    print(f"      Department: {res_data.get('department')}")
    print(f"      Tasks Tracked in DB: {res_data.get('tasks_tracked')}")
    print(f"      Tasks Submitted: {res_data.get('tasks_submitted')}")

    # Step 3: Meta-Orchestrator Requirements Analysis
    print("\n[3/5] Testing Meta-Orchestrator Dynamic Intent Analysis...")
    orchestrator = MetaOrchestrator.get_instance()
    
    test_queries = [
        "Solve my SRM STEP Java assignment and submit to ecurricula",
        "Check NPTEL week 4 assignment deadlines",
        "Build a new react UI dashboard",
        "Create database schema for student grades",
    ]
    for q in test_queries:
        roles = orchestrator._analyze_requirements(q)
        print(f"      Query: '{q[:50]}...' -> Roles: {roles}")

    # Step 4: End-to-End Orchestrated Academic Task Execution
    print("\n[4/5] Executing Autonomous Academic Task via Meta-Orchestrator...")
    orch_task = "Process all pending SRM eCurricula, GCR, Teams, and STEP Java homework"
    orch_result = orchestrator.orchestrate_task(orch_task)

    print(f"      Status: {orch_result.get('status')}")
    print(f"      Agents Provisioned: {orch_result.get('agents_provisioned')}")
    print(f"      Execution Logs:")
    for log in orch_result.get("execution_logs", []):
        print(f"        -> {log}")

    # Step 5: Alfred Central Registry Discovery
    print("\n[5/5] Alfred AgentRegistry Discovery Validation...")
    registry = AgentRegistry()
    registry.register(academic_agent)
    matched = registry.discover("srm_step_java_solver")
    print(f"      Agents with capability 'srm_step_java_solver': {matched}")

    elapsed = round(time.time() - start_time, 2)
    print_banner(f"ORCHESTRATION DEMO COMPLETE IN {elapsed}s — ALL SYSTEMS NOMINAL")


if __name__ == "__main__":
    asyncio.run(run_live_fleet_demonstration())
