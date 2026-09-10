"""
ASTRA Live Demo — Alfred's GPT-6 Astra-Level Computer Use
==========================================================
Run this script to see Alfred control your computer using Gemini Vision.

Usage:
    python demo_astra.py
    python demo_astra.py "Open Notepad and write Hello World"
    python demo_astra.py "Search Google for SRM University BDA course"

Requirements:
    pip install mss pyautogui google-generativeai Pillow
    Set GEMINI_API_KEY environment variable
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# ── Allow running from project root ──────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / "src"))

from jarvisx.computer_use.astra_agent import AstraAgent, get_astra


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          ASTRA — Alfred's Screen-to-Action Agent             ║
║      Gemini Vision  +  Real OS Control  =  Astra Level       ║
╚══════════════════════════════════════════════════════════════╝
""")


def check_prerequisites():
    issues = []

    try:
        import mss
    except ImportError:
        issues.append("mss not installed — run: pip install mss")

    try:
        import pyautogui
    except ImportError:
        issues.append("pyautogui not installed — run: pip install pyautogui")

    try:
        import google.generativeai
    except ImportError:
        issues.append("google-generativeai not installed — run: pip install google-generativeai")

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        issues.append("GEMINI_API_KEY not set — run: $env:GEMINI_API_KEY='your-key-here'")

    return issues


def print_mission_report(mission):
    print("\n" + "═" * 62)
    print(f"  MISSION REPORT")
    print("═" * 62)
    print(f"  ID:       {mission.mission_id}")
    print(f"  Goal:     {mission.goal}")
    print(f"  Status:   {mission.final_status}")
    print(f"  Success:  {'✅ YES' if mission.success else '❌ NO'}")
    print(f"  Steps:    {len(mission.steps)}")
    print(f"  Duration: {mission.total_duration_ms:.0f}ms ({mission.total_duration_ms/1000:.1f}s)")
    if mission.summary:
        print(f"  Summary:  {mission.summary}")
    print("═" * 62)

    print("\n  Step-by-Step Log:")
    for step in mission.steps:
        a = step.action
        coords = f" @ ({a.x},{a.y})" if a.x else ""
        text   = f" → {a.text!r}" if a.text else ""
        keys   = f" [{'+'.join(a.keys)}]" if a.keys else ""
        print(f"  [{step.step:02d}] {a.action_type.upper():16s}{coords}{text}{keys}")
        print(f"       {a.reasoning[:70]}")
        print(f"       Status: {step.result_status} | {step.duration_ms:.0f}ms")

    print("═" * 62 + "\n")


async def main():
    print_banner()

    # Check prereqs
    issues = check_prerequisites()
    if issues:
        print("⚠️  PREREQUISITE ISSUES:")
        for i in issues:
            print(f"   • {i}")
        print()

        # If only API key missing, we can still do a dry-run demo
        if any("GEMINI_API_KEY" in i for i in issues):
            print("Running in DRY-RUN mode (no Gemini API key).")
            print("Screen capture and pyautogui control are still demonstrated.\n")
        else:
            print("Install missing packages then re-run.")
            return

    # Parse goal from command line or use default
    goal = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

    if not goal:
        print("Available demo tasks:")
        print("  1. Open Notepad and type 'Alfred was here'")
        print("  2. Open Chrome and go to youtube.com")
        print("  3. Take a screenshot and save it")
        print("  4. Enter custom goal")
        print()
        choice = input("Pick 1-4 (or press Enter for task 1): ").strip() or "1"

        demos = {
            "1": "Open Notepad using Win+R, type notepad, press Enter, then type 'Alfred was here — powered by ASTRA'",
            "2": "Open Chrome browser and navigate to youtube.com",
            "3": "Take a screenshot of the current desktop and report what apps are visible",
            "4": None,
        }

        if choice == "4":
            goal = input("Enter your goal: ").strip()
        else:
            goal = demos.get(choice, demos["1"])

    print(f"\n🎯 Goal: {goal}")

    # Warn user
    print("\n⚠️  ASTRA will now control your mouse and keyboard.")
    print("   Move mouse to TOP-LEFT corner at any time to emergency-stop (pyautogui FAILSAFE).")
    print()
    countdown = 3
    for i in range(countdown, 0, -1):
        print(f"   Starting in {i}...", end="\r")
        await asyncio.sleep(1)
    print("   Executing now!       \n")

    api_key = os.getenv("GEMINI_API_KEY", "")
    agent = AstraAgent(
        api_key   = api_key if api_key else None,
        max_steps = 12,
        verbose   = True,
    )

    # Run the mission
    start = time.time()
    mission = await agent.run(goal)
    elapsed = time.time() - start

    print_mission_report(mission)

    # Save report
    report_path = Path("var/runtime/astra_reports")
    report_path.mkdir(parents=True, exist_ok=True)
    report_file = report_path / f"{mission.mission_id}.json"

    import json
    from dataclasses import asdict
    report_data = {
        "mission_id":        mission.mission_id,
        "goal":              mission.goal,
        "final_status":      mission.final_status,
        "success":           mission.success,
        "total_duration_ms": mission.total_duration_ms,
        "summary":           mission.summary,
        "steps": [
            {
                "step":           s.step,
                "action_type":    s.action.action_type,
                "x":              s.action.x,
                "y":              s.action.y,
                "text":           s.action.text,
                "keys":           s.action.keys,
                "reasoning":      s.action.reasoning,
                "result_status":  s.result_status,
                "duration_ms":    s.duration_ms,
            }
            for s in mission.steps
        ],
    }
    report_file.write_text(json.dumps(report_data, indent=2))
    print(f"  Report saved: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
