import asyncio
from jarvisx.runtime import create_default_runtime
from jarvisx.agents.alfred import Intent
from jarvisx.core.events import Event

async def run_demonstration():
    print("==================================================")
    print(" JARVIS X: SINGLE ALFRED CAPABILITY ARCHITECTURE")
    print("==================================================\n")
    
    # 1. Initialize Runtime
    runtime = create_default_runtime()
    
    # Give the capability registry a moment to log its discoveries
    await asyncio.sleep(0.5)
    
    # We will simulate the internal routing done by Alfred/Planner to the CapabilityAgent
    print("\n[Demo 1] User: Alfred, open GitHub and search for LangGraph.")
    
    # Create the task payload simulating what the Planner would deduce
    browser_task = Event(
        type="agent.task.requested",
        source="alfred",
        target="capability_engine",
        payload={
            "capability_name": "BROWSER",
            "task": {
                "action": "search",
                "query": "LangGraph on GitHub"
            }
        }
    )
    
    print("[OK] Intent understood")
    print("[OK] Capability selected: Browser")
    print("[OK] Provider selected: Chrome")
    responses = await runtime.hermes.publish(browser_task)
    for response in responses:
        print(f"Alfred: {response.message}")
        
        
    print("\n[Demo 2] User: Alfred, create a folder named Demo.")
    fs_task = Event(
        type="agent.task.requested",
        source="alfred",
        target="capability_engine",
        payload={
            "capability_name": "FILE_SYSTEM",
            "task": {
                "action": "create_folder",
                "target": "DemoFolder"
            }
        }
    )
    
    print("[OK] Intent understood")
    print("[OK] Capability selected: File System")
    responses = await runtime.hermes.publish(fs_task)
    for response in responses:
        print(f"Alfred: {response.message}")
        
        
    print("\n[Demo 3] User: Alfred, open VS Code and continue working on Jarvis X.")
    desktop_task = Event(
        type="agent.task.requested",
        source="alfred",
        target="capability_engine",
        payload={
            "capability_name": "DESKTOP",
            "task": {
                "action": "open",
                "target": "vscode"
            }
        }
    )
    
    print("[OK] Intent understood")
    print("[OK] Capability selected: Desktop")
    print("[OK] Provider discovered")
    responses = await runtime.hermes.publish(desktop_task)
    for response in responses:
        print(f"Alfred: {response.message}")
        
    print("\n==================================================")
    print(" DEMONSTRATION COMPLETE")
    print("==================================================")
    
    # Clean up Demo Folder
    import shutil
    from pathlib import Path
    demo_path = Path("DemoFolder")
    if demo_path.exists():
        shutil.rmtree(demo_path)

if __name__ == "__main__":
    asyncio.run(run_demonstration())
