"""Phase 11 Observable Multi-Agent Reality Test (Visual Edition)."""
import os
import sys
import time
import json
import asyncio
import signal
import subprocess
from typing import Dict, Any, List

from jarvisx.core.agents.agent_identity import AgentIdentity, AgentState
from jarvisx.core.agents.agent_registry import AgentRegistry
from jarvisx.core.agents.agent_coordinator import AgentCoordinator
from jarvisx.core.agents.message_bus import MessageBus, Message
from jarvisx.core.agents.resource_manager import ResourceManager
from jarvisx.core.tools.tool_registry import ToolRegistry


async def kill_writer_midway(writer_proc: subprocess.Popen):
    """Forcefully terminate WriterAgent midway through execution to prove recovery."""
    await asyncio.sleep(5.0)  # Wait for it to start working
    if writer_proc.poll() is None:
        print(f"\n[!] SABOTAGE: Terminating WriterAgent (PID {writer_proc.pid}) forcefully...")
        writer_proc.terminate()
        # Ensure it's dead
        try:
            os.kill(writer_proc.pid, signal.SIGTERM)
        except Exception:
            pass


async def run_demo():
    # 1. Clear directories
    import shutil
    for d in ["var/message_bus", "var/locks", "var/heartbeats"]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)
    os.makedirs("var/message_bus/history", exist_ok=True)
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

    # 3. Spawn independent OS processes in NEW CONSOLES
    print("\nSpawning agent processes in separate terminal windows...")
    processes = {}
    creationflags = 0
    if os.name == 'nt':
        creationflags = subprocess.CREATE_NEW_CONSOLE

    for agent_id, cap, tool, sleep_t in agents_config:
        cmd = [sys.executable, "visual_agent.py", agent_id, tool, str(sleep_t)]
        
        # Set PYTHONPATH so the agent can find jarvisx module
        env = os.environ.copy()
        env["PYTHONPATH"] = "src"
        
        p = subprocess.Popen(cmd, env=env, creationflags=creationflags)
        processes[agent_id] = p
        
        # Stagger slightly so windows don't all open exactly on top of each other at the exact same millisecond
        time.sleep(0.5)

    # Allow processes to start and draw their UI
    await asyncio.sleep(2.0)

    # 4. Start Saboteur
    saboteur_task = asyncio.create_task(kill_writer_midway(processes["writer_agent"]))

    # 5. Coordinator execution
    tool_registry = ToolRegistry.get_instance()
    coordinator = AgentCoordinator(agent_registry, tool_registry)
    message_bus = MessageBus.get_instance()
    
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
    
    print("\n========== MULTI-AGENT EXECUTION COMPLETE ==========")
    print(json.dumps(results, indent=2))
    
    # Final check
    if results["success"]:
        print("\n[SUCCESS] Objective completed successfully with failure recovery.")
    else:
        print("\n[FAILED] Objective did not complete.")
        
    print("\nInstructing agents to hold for 30 seconds before closing...")
    # Send custom SHUTDOWN message directly using MessageBus
    # We bypass MessageType enum validation since we defined a custom string in visual_agent.py
    for agent_id in processes.keys():
        await message_bus.send(Message(
            sender_id="coordinator",
            recipient_id=agent_id,
            msg_type="SHUTDOWN",  # Our custom type that visual_agent checks for
            payload={}
        ))
    
    print("Main process will exit now. Watch the agent terminals.")

if __name__ == "__main__":
    asyncio.run(run_demo())
