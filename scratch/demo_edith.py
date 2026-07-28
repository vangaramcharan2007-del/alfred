import asyncio
import os
import sys

# Ensure imports work from the root of the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from jarvisx.agents.edith import EdithAgent
from jarvisx.core.events import Event
from jarvisx.tools.termux import TermuxTool

async def main():
    print("\n--- PHASE EDITH UNLEASHED SIMULATION ---")
    
    # We set ADB target to none so it simulates instead of actually crashing if ADB isn't connected
    os.environ["JARVIS_ADB_TARGET"] = ""
    
    tools = {
        "termux": TermuxTool()
    }
    
    edith = EdithAgent(tools=tools)
    
    print("\n[User]: Edith, what is my phone battery at?")
    event1 = Event(type="intent", source="user", payload={"message": "battery"})
    resp1 = await edith.handle(event1)
    print(f"[Edith Result]: {resp1.data}")
    
    print("\n[User]: Edith, remind me to drink water in 0.1 minutes.")
    event2 = Event(type="intent", source="user", payload={"message": "remind"})
    resp2 = await edith.handle(event2)
    print(f"[Edith Result]: {resp2.data}")
    
    print("\n[System]: Waiting 7 seconds to let background reminder trigger...")
    await asyncio.sleep(7)
    
    print("\n[System]: Simulation complete.")

if __name__ == "__main__":
    asyncio.run(main())
