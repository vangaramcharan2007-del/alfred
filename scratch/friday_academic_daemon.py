import sys
import os
import json
import time
import asyncio

sys.path.insert(0, 'src')
from jarvisx.runtime import create_default_runtime
from jarvisx.tools.missions import MissionTool
from jarvisx.tools.memory import LocalMemoryTool

def setup_missions():
    memory = LocalMemoryTool()
    mission_tool = MissionTool(memory_tool=memory)
        
    active_missions = mission_tool.list_active_missions().data.get("active_missions", [])
    cgpa_exists = any("10 CGPA" in m["title"] for m in active_missions)
    
    if not cgpa_exists:
        print("[*] Generating 10 CGPA Main Quest...")
        mission_tool.create_mission(
            title="Achieve 10 CGPA (Semester 3)",
            mission_type="main_quest",
            description="Master Maths, AOOP, and DSA using prescribed resources."
        )
        mission_tool.create_mission(
            title="DSA LeetCode Grind",
            mission_type="daily_mission",
            description="Solve 2 LeetCode problems."
        )
        mission_tool.create_mission(
            title="AOOP NPTEL Prep",
            mission_type="daily_mission",
            description="Watch 1 NPTEL video for Advanced Object-Oriented Programming."
        )
        mission_tool.create_mission(
            title="Maths Transforms",
            mission_type="daily_mission",
            description="Watch 1 video from E Suresh playlist."
        )
        print("[*] Missions generated successfully.")
    else:
        print("[*] Academic missions already exist.")

def active_interruption(runtime):
    print("\n==========================================")
    print("--- FRIDAY ACADEMIC DAEMON INTERRUPT ---")
    print("==========================================")
    print("\a") # Bell sound
    print("[Friday]: Sir, it is time for your scheduled study session.")
    print("[Friday]: Based on your timetable, you have Data Structures and Algorithms now.")
    print("[Friday]: I am opening LeetCode and checking your daily missions.")
    
    async def simulate_friday():
        response = await runtime.alfred.process("friday, check my DSA mission and open leetcode", trace_id="academic-1")
        print("\n--- Friday Execution ---")
        print(response.message)
        print("------------------------")

    asyncio.run(simulate_friday())

if __name__ == "__main__":
    print("[*] Booting Academic Daemon...")
    runtime = create_default_runtime()
    setup_missions()
    
    print("\n[*] Academic daemon running in background...")
    time.sleep(2) # Simulate wait for schedule
    active_interruption(runtime)
    
    pass
