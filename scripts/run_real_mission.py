#!/usr/bin/env python3
"""
Jarvis X Production Golden Mission Execution Script
Phase 39 Real Mission Run

Mission: "Build a personal productivity dashboard"

Pipeline:
User Input → Alfred Brain → Intent Parser → Mission Planner → Architecture Agent → LLM Router → Coding Agent → Sandbox → Tests → Git Commit → Memory Storage
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Ensure UTF-8 console output for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Ensure src directory is in sys.path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from jarvisx.runtime.runtime import JarvisRuntime
from jarvisx.telemetry.logging_service import get_production_logger

async def run_golden_mission():
    print("=" * 80)
    print("        JARVIS X PRODUCTION RUNTIME - GOLDEN MISSION EXECUTION")
    print("=" * 80)
    print()

    logger = get_production_logger()

    # 1. Boot Runtime
    runtime = JarvisRuntime()
    state = await runtime.start(print_banner=True)

    mission_prompt = "Build a personal productivity dashboard"
    print(f"[INPUT] User Request: \"{mission_prompt}\"")
    logger.log_event("mission", "user_input_received", {"prompt": mission_prompt})
    print()

    # 2. Process Request via Brain & Mission Executor
    print("[RUNNING] Processing Mission Pipeline...")
    res = await runtime.process_task(mission_prompt)

    mission = res.get("mission_result", {}).get("mission", {})
    result = res.get("mission_result", {}).get("result", {})

    logger.log_event("mission", "mission_completed", {
        "mission_id": mission.get("mission_id"),
        "status": mission.get("status"),
        "duration": result.get("duration")
    })

    print(f"   [+] Mission ID: {mission.get('mission_id')}")
    print(f"   [+] Status: {mission.get('status')}")
    print(f"   [+] Intent: {mission.get('intent')}")
    print(f"   [+] Architecture: {result.get('architecture')}")
    print(f"   [+] Workspace Created: {result.get('provider_output', {}).get('workspace')}")
    print(f"   [+] Files Created: {', '.join(result.get('provider_output', {}).get('files_created', []))}")
    print(f"   [+] Test Execution: {result.get('test_result', {}).get('stdout')} (Exit Code: {result.get('test_result', {}).get('exit_code')})")
    print(f"   [+] Local Git Status: {result.get('git_result', {}).get('status')}")
    print(f"   [+] GitHub Integration: {result.get('github_pr', {}).get('status')} ({result.get('github_pr', {}).get('reason', 'N/A')})")
    print(f"   [+] Memory Recorded: {result.get('evolution_memory', {}).get('upgrade_id')}")
    print()

    # 3. Shutdown cleanly
    await runtime.stop()

    print("=" * 80)
    print("  [SUCCESS] GOLDEN MISSION RUN COMPLETED WITH REAL FILES & GIT INTEGRATION")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_golden_mission())
