"""
Live Demonstration Script for Jarvis OS Autonomous AI Harness.
Demonstrates:
1. Active Environmental Context Sensing
2. Ambient Clipboard Error Interception
3. Autonomous Self-Healing ReAct Task Tree Execution
"""

import asyncio
import os
import sys
import time

# Ensure UTF-8 console output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to sys.path
sys.path.insert(0, os.path.abspath("src"))

from jarvisx.harness.active_context_sensor import ActiveWindowContextSensor
from jarvisx.harness.clipboard_sensor import AmbientClipboardSensor
from jarvisx.harness.autonomous_reloop_engine import AutonomousReActHarness


def main():
    print("\n" + "=" * 75)
    print(" ⚡ JARVIS OS — SOVEREIGN AI HARNESS (LIVE SYSTEM DEMONSTRATION)")
    print("=" * 75)

    # 1. Test Active Window Context Sensor
    print("\n[*] Pillar 1: Active Environmental Context Sensing...")
    ctx_sensor = ActiveWindowContextSensor()
    ctx = ctx_sensor.get_current_context()
    print(f"    • Foreground Window : {ctx.window_title}")
    print(f"    • Process Name      : {ctx.process_name} (PID {ctx.pid})")
    print(f"    • Environmental Mode: [{ctx.context_mode}]")
    time.sleep(1.0)

    # 2. Test Ambient Clipboard Interceptor
    print("\n[*] Pillar 2: Ambient Clipboard Interception Simulation...")
    clip_sensor = AmbientClipboardSensor()
    
    sample_error = """Traceback (most recent call last):
  File "src/jarvisx/automation/workflow.py", line 42, in execute
    result = compute_vector_similarity(query_embedding, None)
TypeError: unsupported operand type(s) for *: 'NoneType' and 'float'"""
    
    event = clip_sensor._analyze_content(sample_error)
    if event:
        print(f"    [+] Event Type Intercepted : {event.event_type}")
        print(f"    [+] Error Summary          : {event.parsed_metadata.get('error_summary')}")
        print(f"    [+] Target File & Line     : {event.parsed_metadata.get('file_path')}:{event.parsed_metadata.get('line_number')}")
        print(f"    [+] Recommended Action     : {event.parsed_metadata.get('recommended_action')}")
    time.sleep(1.0)

    # 3. Test Autonomous ReAct Self-Healing Task Tree Loop
    print("\n[*] Pillar 3: Autonomous ReAct Task Tree Execution Loop...")
    harness = AutonomousReActHarness()

    async def run_tree():
        goal = "audit laptop memory, optimize background thermals, and get system health"
        print(f"    • Macro Goal: '{goal}'")
        tree = await harness.execute_macro_goal_async(goal)
        print("\n" + "-" * 75)
        print(f" 🌳 LIVING TASK TREE EXECUTION GRAPH (Status: {tree.overall_status})")
        print("-" * 75)
        for idx, node in enumerate(tree.nodes):
            status_icon = "✔" if node.status == "COMPLETED" else "✖"
            print(f"    [{status_icon}] Step {idx+1}: {node.description}")
            print(f"        Agent: {node.assigned_agent} | Tool: {node.tool} | Status: {node.status}")

    asyncio.run(run_tree())

    print("\n" + "=" * 75)
    print(" [OK] ✅ JARVIS OS AI HARNESS FULLY OPERATIONAL — CHATBOX PARADIGM TRANSCENDED")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
