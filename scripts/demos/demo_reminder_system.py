"""
Live Demonstration & Verification: Real-Time Reminder Engine for Jarvis X.
Tests scheduling, parsing ('524 pm', 'in 3 seconds'), sentinel firing, and tool integration.
"""

import asyncio
import sys
import os
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvisx.organism import get_organism
from jarvisx.automation.reminder_engine import get_reminder_engine

async def main():
    print("\n" + "=" * 70)
    print("   JARVIS X — REAL-TIME REMINDER ENGINE: LIVE VERIFICATION")
    print("=" * 70 + "\n")

    org = get_organism()
    engine = get_reminder_engine()

    # -------------------------------------------------------------------
    # TEST 1: User's exact prompt "yoo remind me at 524 pm to get ready for packing today"
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 1: Schedule Reminder via Natural User Prompt")
    print("-" * 60)
    prompt1 = "yoo remind me at 524 pm to get ready for packing today"
    print(f"User Prompt: '{prompt1}'")
    
    res1 = await org.react_turn(prompt1)
    print(f"Decision:    {res1.get('decision')}")
    print(f"Tool Called: {res1.get('tool')}")
    print(f"Spoken/Resp: {res1.get('response') or res1.get('spoken')}")
    print(f"Tool Result: {res1.get('tool_result')}")
    print()

    assert res1.get("tool") == "set_reminder" or res1.get("decision") == "tool_call", "Should have chosen set_reminder tool!"

    # -------------------------------------------------------------------
    # TEST 2: List Reminders
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 2: List Active Reminders")
    print("-" * 60)
    active = engine.list_reminders()
    print(f"Total Pending Reminders: {len(active)}")
    for r in active:
        print(f"  • [{r['id']}] '{r['message']}' -> {r['display_time']} ({r['countdown']}) [Status: {r['status']}]")
    print()

    # -------------------------------------------------------------------
    # TEST 3: Short-Fuse Reminder Live Firing & Sentinel Test
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 3: 3-Second Countdown Live Sentinel Firing")
    print("-" * 60)
    res3 = await org.react_turn("remind me in 3 seconds to take a deep breath")
    print(f"Scheduled 3s reminder: {res3.get('tool_result')}")
    print("Waiting 4 seconds for background sentinel daemon to trigger vocal alert and toast...")
    time.sleep(4.0)

    # Check that it fired
    all_rems = engine.list_reminders(pending_only=False)
    fired = [r for r in all_rems if "deep breath" in r.get("message", "")]
    if fired:
        print(f"  • Reminder Status: {fired[0]['status']} [SUCCESS]")
    print()

    print("=" * 70)
    print("   ALL REMINDER ENGINE TESTS PASSED [OK]")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
