"""
Live Verification: Autonomous Continuous Engineering Sentinel.
"""

import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvisx.organism import get_organism
from jarvisx.engineering.autonomous_engineering_daemon import get_engineering_sentinel

async def main():
    print("=" * 70)
    print("   ALFRED OS — CONTINUOUS ENGINEERING SENTINEL VERIFICATION")
    print("=" * 70 + "\n")

    org = get_organism()
    sentinel = get_engineering_sentinel()

    # -------------------------------------------------------------------
    # TEST 1: User's Natural Prompt via Living Organism
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 1: Natural Explanation of Continuous vs Directive Modes")
    print("-" * 60)
    prompt = "SO HOW DOES THIS AGENT CONTINUOSLY WRK OR I SHOULD GIVE THE REPO NAME"
    res1 = await org.react_turn(prompt)
    print(f"Decision: {res1.get('decision')}")
    print(f"Spoken/Response:\n{res1.get('response') or res1.get('spoken')}\n")

    # -------------------------------------------------------------------
    # TEST 2: Sentinel Activation & Status Query
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 2: Start & Query Autonomous Engineering Sentinel")
    print("-" * 60)
    start_res = sentinel.start_sentinel()
    print(f"Start Status:  {start_res}")
    assert start_res.get("status") in ("started", "already_running")

    status_res = sentinel.get_status()
    print(f"Daemon Status: {status_res}")
    assert status_res.get("status") == "running"

    print("\n" + "=" * 70)
    print("   ALL CONTINUOUS SENTINEL TESTS PASSED [OK]")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
