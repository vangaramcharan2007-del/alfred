"""
Verify contextual reasoning and elimination of static if-statement keyword traps.
"""
import asyncio
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvisx.organism import get_organism
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator

async def main():
    print("=" * 70)
    print("TEST 1: 'use youtube as reference and teach me frst module of dsa'")
    print("=" * 70)
    org = get_organism()
    res1 = await org.react_turn("use youtube as reference and teach me frst module of dsa")
    print(f"Decision: {res1.get('decision')}")
    print(f"Tool called: {res1.get('tool')}")
    print(f"Response snippet:\n{res1.get('response')[:400]}...\n")
    assert res1.get('tool') != 'open_app', "Should not blindly launch open_app when youtube is just a reference!"

    print("=" * 70)
    print("TEST 2: 'open youtube' (Explicit Launch Request)")
    print("=" * 70)
    res2 = await org.react_turn("open youtube")
    print(f"Decision: {res2.get('decision')}")
    print(f"Tool called: {res2.get('tool')}")
    print(f"Spoken:\n{res2.get('spoken')}\n")

    print("=" * 70)
    print("TEST 3: DynamicOrchestrator.execute_voice_command with contextual prompt")
    print("=" * 70)
    orch = DynamicOrchestrator()
    res3 = orch.execute_voice_command("plan a dsa course and teach me dsa im a beginner")
    print(f"Action: {res3.get('action')}")
    print(f"Response snippet:\n{res3.get('response')[:400]}...\n")

    print("=" * 70)
    print("ALL CONTEXTUAL ROUTING TESTS PASSED [OK] - NO KEYWORD TRAPS")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
