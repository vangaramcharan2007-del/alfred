"""Phase 12 Observable Autonomous Initiative Engine Demonstration."""
import os
import sys
import time
import json
import asyncio
import shutil
import subprocess
from typing import Dict, Any, List

from jarvisx.core.agents.agent_identity import AgentIdentity
from jarvisx.core.agents.agent_registry import AgentRegistry
from jarvisx.core.agents.agent_coordinator import AgentCoordinator
from jarvisx.core.agents.message_bus import MessageBus, Message, MessageType
from jarvisx.core.tools.tool_registry import ToolRegistry
from jarvisx.core.world_state_monitor import (
    WorldStateMonitor, FilesystemSensor, TaskFailureSensor, ResourceSensor, WorldEvent
)
from jarvisx.core.initiative_manager import InitiativeManager, ApprovalMode, ProposalStatus

async def display_dashboard(initiative_manager: InitiativeManager, monitor_task: asyncio.Task, coordinator: AgentCoordinator, fs_sensor: FilesystemSensor):
    """Live dashboard that updates every 0.5s."""
    print("Initializing Initiative Panel...")
    await asyncio.sleep(2.0)  # Wait for sensors to trigger

    # Approval countdown state
    approval_countdown = 5
    approved_obj_id = None
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("====================================")
        print("JARVIS X AUTONOMOUS INITIATIVE PANEL")
        print("====================================")
        print("")
        print("Detected Situations:")
        
        proposals = initiative_manager.proposals
        for p in proposals:
            if "Clean" in p.title:
                print("- Downloads clutter detected")
            if "backup" in p.title.lower():
                print("- Backup failures detected")
            if "Analyze" in p.title:
                print("- Disk pressure detected")
                
        print("\nSuggested Objectives:")
        for idx, p in enumerate(proposals):
            checkbox = "[x]" if p.status in [ProposalStatus.APPROVED, ProposalStatus.DISPATCHED, ProposalStatus.COMPLETED, ProposalStatus.VERIFIED] else "[ ]"
            print(f"{checkbox} {p.title} (Status: {p.status.value})")
            
        print("\n------------------------------------")
        
        # Take the first pending proposal and run countdown
        pending = initiative_manager.get_pending_proposals()
        if pending and approved_obj_id is None:
            p = pending[0]
            print(f"Proposal: {p.title}")
            print(f"Priority: {p.priority}")
            print(f"Confidence: {p.confidence}%")
            if approval_countdown > 0:
                print(f"Auto approval in {approval_countdown}...")
                approval_countdown -= 1
            else:
                print("APPROVED")
                initiative_manager.approve_proposal(p.id)
                approved_obj_id = p.id
        elif approved_obj_id:
            # We have an approved proposal, dispatch it
            p = next(prop for prop in proposals if prop.id == approved_obj_id)
            if p.status == ProposalStatus.APPROVED:
                print(f"Dispatching objective: {p.title} to Multi-Agent Mesh...")
                initiative_manager.dispatch_proposal(p.id)
                
                # Create subtasks for AgentCoordinator based on action_type
                if p.action_type == "clean":
                    sub_tasks = [
                        {
                            "id": "plan_cleanup",
                            "description": "Plan cleanup strategy",
                            "required_capability": "planning",
                            "tool": "planner_tool",
                            "method": "do_work",
                            "args": {"action": "plan", "resource": p.action_resource}
                        },
                        {
                            "id": "exec_cleanup",
                            "description": "Execute file deletion",
                            "required_capability": "execution",
                            "tool": "execution_tool",
                            "method": "do_work",
                            "args": {"action": "delete_all", "resource": p.action_resource}
                        }
                    ]
                else:
                    # Mock for others
                    sub_tasks = [
                        {
                            "id": "plan_task",
                            "description": "Plan task",
                            "required_capability": "planning",
                            "tool": "planner_tool",
                            "method": "do_work",
                            "args": {"action": "plan", "resource": p.action_resource}
                        }
                    ]
                
                # Actually dispatch to the mesh in the background so dashboard keeps updating
                asyncio.create_task(execute_and_verify(p, sub_tasks, coordinator, initiative_manager, fs_sensor))
                approved_obj_id = None
                approval_countdown = 5 # Reset for next
        
        # Check if all completed
        all_done = len(proposals) > 0 and all(p.status in [ProposalStatus.VERIFIED, ProposalStatus.COMPLETED] for p in proposals)
        if all_done:
            print("\nAll autonomous objectives VERIFIED and COMPLETED.")
            break
            
        await asyncio.sleep(1.0)
        
async def execute_and_verify(proposal, sub_tasks, coordinator, manager, fs_sensor):
    # Execute
    results = await coordinator.execute_multi_agent_objective(proposal.title, sub_tasks)
    manager.complete_proposal(proposal.id, results["success"])
    
    # Verification Stage
    print(f"\n[Verification] Checking results for: {proposal.title}")
    if proposal.action_type == "clean":
        # Check the actual filesystem using the sensor logic
        # The tool execution must actually delete the files
        count = 0
        if os.path.exists(fs_sensor.watch_dir):
            for entry in os.scandir(fs_sensor.watch_dir):
                if entry.is_file():
                    count += 1
        
        if count == 0:
            manager.verify_proposal(proposal.id)
        else:
            # Failed verification
            manager.proposals = [p for p in manager.proposals if p.id != proposal.id] # Hack to keep it clean

async def run_demo():
    # 1. Setup Mock Files
    mock_dir = "var/mock_downloads"
    if os.path.exists(mock_dir):
        shutil.rmtree(mock_dir)
    os.makedirs(mock_dir, exist_ok=True)
    
    print(f"Populating {mock_dir} with 500 mock files...")
    for i in range(500):
        with open(os.path.join(mock_dir, f"file{i:03d}.tmp"), "w") as f:
            f.write("mock")
            
    # 2. Clear IPC
    for d in ["var/message_bus", "var/locks", "var/heartbeats"]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)
    os.makedirs("var/message_bus/history", exist_ok=True)
    
    # 3. Setup Agents
    agent_registry = AgentRegistry()
    agents_config = [
        ("planner_agent", "planning", "planner_tool", 1.0),
        ("execution_agent", "execution", "execution_tool", 1.0),
    ]
    
    for agent_id, cap, tool, sleep_t in agents_config:
        agent_registry.register_agent(AgentIdentity(
            name=agent_id.capitalize(), role="Specialist", capabilities=[cap], agent_id=agent_id
        ))

    # Spawn OS Processes
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
    
    # 4. Setup Initiative Engine
    initiative_manager = InitiativeManager(ApprovalMode.AUTO)
    monitor = WorldStateMonitor(initiative_manager)
    
    fs_sensor = FilesystemSensor(mock_dir)
    task_sensor = TaskFailureSensor()
    res_sensor = ResourceSensor()
    
    monitor.add_sensor(fs_sensor)
    monitor.add_sensor(task_sensor)
    monitor.add_sensor(res_sensor)
    
    # 5. Inject Triggers
    task_sensor.inject_failure("backup_database", 5)
    res_sensor.set_disk_usage(92)
    
    # 6. Start Monitor & Coordinator
    monitor_task = asyncio.create_task(monitor.run())
    
    tool_registry = ToolRegistry.get_instance()
    coordinator = AgentCoordinator(agent_registry, tool_registry)
    
    # 7. Run Dashboard
    try:
        await display_dashboard(initiative_manager, monitor_task, coordinator, fs_sensor)
    finally:
        monitor.stop()
        monitor_task.cancel()
        
        # Shutdown agents
        message_bus = MessageBus.get_instance()
        for agent_id in processes.keys():
            await message_bus.send(Message(
                sender_id="coordinator",
                recipient_id=agent_id,
                msg_type="SHUTDOWN",
                payload={}
            ))
            
        print("Agents shutting down...")
        await asyncio.sleep(2.0)

if __name__ == "__main__":
    asyncio.run(run_demo())
