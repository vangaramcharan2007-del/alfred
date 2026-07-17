"""Phase 13: Persistent Goal & Mission Continuity Demonstration."""
import os
import sys
import time
import asyncio
import subprocess

from typing import Dict, Any

from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.mission_continuity import MissionContinuityManager
from jarvisx.core.initiative_manager import InitiativeManager, ApprovalMode, ProposalStatus
from jarvisx.core.agents.agent_identity import AgentIdentity
from jarvisx.core.agents.agent_registry import AgentRegistry
from jarvisx.core.agents.agent_coordinator import AgentCoordinator
from jarvisx.core.agents.message_bus import MessageBus, Message, MessageType
from jarvisx.core.tools.tool_registry import ToolRegistry

async def spawn_agents():
    agent_registry = AgentRegistry()
    agents_config = [
        ("planner_agent", "planning", "planner_tool", 0.5),
        ("execution_agent", "execution", "execution_tool", 1.0),
    ]
    
    for agent_id, cap, tool, sleep_t in agents_config:
        agent_registry.register_agent(AgentIdentity(
            name=agent_id.capitalize(), role="Specialist", capabilities=[cap], agent_id=agent_id
        ))

    print("\nSpawning execution agents in background terminals...")
    processes = {}
    creationflags = subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    
    for agent_id, cap, tool, sleep_t in agents_config:
        cmd = [sys.executable, "visual_agent.py", agent_id, tool, str(sleep_t)]
        processes[agent_id] = subprocess.Popen(cmd, env=env, creationflags=creationflags)
        time.sleep(0.5)
        
    await asyncio.sleep(2.0)
    return agent_registry, processes

async def run1(store: ObjectiveStore):
    print("No active objectives found. Starting RUN 1: Simulating interruption.")
    obj_data = {
        "objective_id": "obj_001",
        "title": "Build Portfolio Website",
        "status": "IN_PROGRESS",
        "progress": 40,
        "assigned_agents": [
            "planner_agent",
            "execution_agent"
        ],
        "last_agent": "execution_agent",
        "last_completed_task": "build_frontend",
        "remaining_tasks": [
            "deploy_frontend",
            "configure_domain",
            "verify_ssl"
        ],
        "recovery_count": 0
    }
    
    print("Planner Agent")
    print("[x] Requirements gathered")
    print("[x] Architecture completed")
    print("[x] Frontend built")
    print("\nSaving objective state...")
    
    store.save_objective(obj_data)
    print("State saved successfully.")
    print("Simulation interrupted intentionally.\nRestart demo to test continuity.")
    sys.exit(0)

async def run2(store: ObjectiveStore, active: list):
    print("=====================================")
    print("JARVIS X CONTINUITY DASHBOARD")
    print("=====================================")
    print("\nRecovered Objectives:")
    print("---------------------")
    
    continuity_manager = MissionContinuityManager(store)
    proposals = continuity_manager.generate_recovery_proposals()
    
    for obj in active:
        print(f"\n{obj['title']}")
        print(f"Progress: {obj['progress']}%")
        print("\nDetected interruption.")
        print(f"\nLast Completed Task:\n{obj.get('last_completed_task', 'None')}")
        print("\nRemaining Tasks:")
        for t in obj.get('remaining_tasks', []):
            print(f"- {t}")
            
    print("\nRecommended action:")
    for p in proposals:
        print(p.description)
        
    print("\nAuto resume in:")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
        
    print("\nRECOVERY APPROVED")
    print("RESUMING OBJECTIVE")
    
    # Spawn real agents and coordinator to resume
    agent_registry, processes = await spawn_agents()
    tool_registry = ToolRegistry.get_instance()
    coordinator = AgentCoordinator(agent_registry, tool_registry)
    
    obj_to_resume = active[0]
    
    sub_tasks = []
    for task_name in obj_to_resume["remaining_tasks"]:
        sub_tasks.append({
            "id": f"task_{task_name}",
            "description": task_name.replace("_", " ").title(),
            "required_capability": "execution",
            "tool": "execution_tool",
            "method": "do_work",
            "args": {"action": "execute", "resource": task_name}
        })
        
    print(f"\nDispatching recovered objective: {obj_to_resume['title']}...")
    print("Planner agent acknowledged.")
    
    results = await coordinator.execute_multi_agent_objective(
        objective=obj_to_resume["title"], 
        sub_tasks=sub_tasks,
        objective_id=obj_to_resume["objective_id"]
    )
    
    for t in sub_tasks:
        print(f"Execution Agent:\n[x] {t['args']['resource']}")
    
    print("\nObjective Progress: 100%")
    print("Status: COMPLETE")
    
    store.complete_objective(obj_to_resume["objective_id"])
    print("Objective archived successfully.")
    
    # Shutdown agents
    message_bus = MessageBus.get_instance()
    for agent_id in processes.keys():
        await message_bus.send(Message(
            sender_id="coordinator",
            recipient_id=agent_id,
            msg_type="SHUTDOWN",
            payload={}
        ))
        
    await asyncio.sleep(2.0)

async def main():
    store = ObjectiveStore()
    active = store.load_active_objectives()
    
    if not active:
        await run1(store)
    else:
        await run2(store, active)

if __name__ == "__main__":
    asyncio.run(main())
