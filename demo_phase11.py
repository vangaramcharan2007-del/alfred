"""Phase 11 Observable Multi-Agent Reality Test."""
import os
import sys
import time
import json
import asyncio
import signal
import multiprocessing
from typing import Dict, Any, List

from jarvisx.core.agents.agent_identity import AgentIdentity, AgentState
from jarvisx.core.agents.agent_registry import AgentRegistry
from jarvisx.core.agents.agent_worker import run_agent_worker
from jarvisx.core.agents.agent_coordinator import AgentCoordinator
from jarvisx.core.agents.message_bus import MessageBus
from jarvisx.core.agents.resource_manager import ResourceManager
from jarvisx.core.tools.tool_registry import ToolRegistry


class DemoTool:
    """A mock tool to simulate work for the demonstration."""
    def __init__(self, name: str, sleep_time: float = 2.0):
        self.name = name
        self.sleep_time = sleep_time
        
    def do_work(self, action: str, resource: str):
        # Simulate work
        time.sleep(self.sleep_time)
        return {"success": True, "evidence": {"action": action, "resource": resource}}


def worker_process(agent_id: str, tool_name: str, sleep_time: float = 2.0):
    """Entry point for independent OS agent processes."""
    registry = ToolRegistry.get_instance()
    # Register the tool the agent uses
    registry.register(DemoTool(tool_name, sleep_time), tool_name)
    run_agent_worker(agent_id)


async def live_dashboard(processes: Dict[str, multiprocessing.Process]):
    """Visible console window showing active agents, PIDs, locks, and heartbeats."""
    resource_manager = ResourceManager.get_instance()
    message_bus = MessageBus.get_instance()
    
    print("\nStarting live dashboard...\n")
    try:
        while True:
            # Clear screen (cross-platform)
            os.system('cls' if os.name == 'nt' else 'clear')
            print("================ JARVIS X PHASE 11 DASHBOARD ================")
            print(f"Time: {time.strftime('%H:%M:%S')}")
            print("-------------------------------------------------------------")
            print(f"{'AGENT':<20} | {'PID':<6} | {'STATUS':<8} | {'LOCKS HELD':<15} | {'QUEUED'}")
            print("-------------------------------------------------------------")
            
            locked_resources = resource_manager.get_locked_resources()
            
            for agent_id, proc in processes.items():
                pid = proc.pid if proc.is_alive() else "DEAD"
                
                # Check heartbeat
                status = "OFFLINE"
                heartbeat_file = os.path.join("var", "heartbeats", f"{agent_id}.json")
                if os.path.exists(heartbeat_file):
                    try:
                        with open(heartbeat_file, "r") as f:
                            hb = json.load(f)
                            if time.time() - hb["last_seen"] < 3.0:
                                status = hb.get("status", "RUNNING")
                    except Exception:
                        pass
                
                # Check locks
                locks = [res for res, owner in locked_resources.items() if owner == agent_id]
                locks_str = ",".join(locks) if locks else "None"
                
                # Check queue size
                queued = message_bus.get_pending_count(agent_id)
                
                print(f"{agent_id:<20} | {str(pid):<6} | {status:<8} | {locks_str:<15} | {queued}")
                
            print("=============================================================")
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass


async def kill_writer_midway(writer_proc: multiprocessing.Process):
    """Forcefully terminate WriterAgent midway through execution to prove recovery."""
    await asyncio.sleep(5.0)  # Wait for it to start working
    if writer_proc.is_alive():
        print(f"\n[!] SABOTAGE: Terminating WriterAgent (PID {writer_proc.pid}) forcefully...")
        writer_proc.terminate()
        # Ensure it's dead
        try:
            os.kill(writer_proc.pid, signal.SIGTERM)
        except Exception:
            pass


async def run_demo():
    # 1. Clear directories
    for d in ["var/message_bus", "var/message_bus/history", "var/locks", "var/heartbeats"]:
        os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            if os.path.isfile(os.path.join(d, f)):
                try:
                    os.remove(os.path.join(d, f))
                except Exception:
                    pass

    # 2. Setup Agent Registry
    agent_registry = AgentRegistry()
    agents_config = [
        ("planner_agent", "planning", "planner_tool", 1.0),
        ("research_agent", "research", "research_tool", 2.0),
        ("writer_agent", "writing", "writer_tool", 8.0),       # Takes a long time
        ("reviewer_agent", "reviewing", "reviewer_tool", 1.0), # Will wait for lock
        ("execution_agent", "execution", "execution_tool", 1.0),
        ("backup_writer_agent", "writing", "writer_tool", 2.0) # Backup
    ]
    
    for agent_id, cap, tool, sleep_t in agents_config:
        identity = AgentIdentity(
            name=agent_id.capitalize(),
            role="Specialist",
            capabilities=[cap],
            agent_id=agent_id
        )
        agent_registry.register_agent(identity)

    # 3. Spawn independent OS processes
    processes = {}
    for agent_id, cap, tool, sleep_t in agents_config:
        p = multiprocessing.Process(target=worker_process, args=(agent_id, tool, sleep_t))
        p.start()
        processes[agent_id] = p

    # Allow processes to start
    await asyncio.sleep(1.0)

    # 4. Start Dashboard and Saboteur
    dashboard_task = asyncio.create_task(live_dashboard(processes))
    saboteur_task = asyncio.create_task(kill_writer_midway(processes["writer_agent"]))

    # 5. Coordinator execution
    tool_registry = ToolRegistry.get_instance()
    coordinator = AgentCoordinator(agent_registry, tool_registry)
    
    sub_tasks = [
        {
            "id": "task_1",
            "description": "Creates task graph",
            "required_capability": "planning",
            "tool": "planner_tool",
            "method": "do_work",
            "args": {"action": "plan", "resource": "graph.json"}
        },
        {
            "id": "task_2",
            "description": "Searches repository contents",
            "required_capability": "research",
            "tool": "research_tool",
            "method": "do_work",
            "args": {"action": "search", "resource": "repo_data.json"}
        },
        {
            "id": "task_3",
            "description": "Generates report sections",
            "required_capability": "writing",
            "tool": "writer_tool",
            "method": "do_work",
            "args": {"action": "write", "resource": "report.md"} # Lock contention!
        },
        {
            "id": "task_4",
            "description": "Checks output quality",
            "required_capability": "reviewing",
            "tool": "reviewer_tool",
            "method": "do_work",
            "args": {"action": "review", "resource": "report.md"} # Lock contention!
        },
        {
            "id": "task_5",
            "description": "Creates final files",
            "required_capability": "execution",
            "tool": "execution_tool",
            "method": "do_work",
            "args": {"action": "save", "resource": "final.md"}
        }
    ]

    print("\nDispatching objective to Coordinator...")
    # This will trigger parallel execution
    results = await coordinator.execute_multi_agent_objective("Create a project report", sub_tasks)
    
    # 6. Cleanup
    dashboard_task.cancel()
    
    # Force kill any remaining processes
    for name, p in processes.items():
        if p.is_alive():
            p.terminate()
            
    print("\n========== MULTI-AGENT EXECUTION COMPLETE ==========")
    print(json.dumps(results, indent=2))
    
    # Final check
    if results["success"]:
        print("\n[SUCCESS] Objective completed successfully with failure recovery.")
    else:
        print("\n[FAILED] Objective did not complete.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    asyncio.run(run_demo())
