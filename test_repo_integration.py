"""
Live Verification: Autonomous Git & Repository Integration Capabilities in Alfred OS.
"""

import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvisx.organism import get_organism
from jarvisx.tools.git_repo_integrator import get_git_integrator

async def main():
    print("=" * 70)
    print("   ALFRED OS — REPOSITORY INTEGRATION: LIVE VERIFICATION")
    print("=" * 70 + "\n")

    org = get_organism()
    integrator = get_git_integrator()

    # -------------------------------------------------------------------
    # TEST 1: User's exact prompt
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 1: 'alfred can u get integrate repos if i say so'")
    print("-" * 60)
    prompt1 = "alfred can u get integrate repos if i say so"
    res1 = await org.react_turn(prompt1)
    print(f"Decision: {res1.get('decision')}")
    print(f"Response snippet:\n{res1.get('response') or res1.get('spoken')}\n")

    # -------------------------------------------------------------------
    # TEST 2: Inspect Current Workspace via IntegrateRepoTool
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 2: Integrate Current Workspace Repository")
    print("-" * 60)
    res2 = integrator.integrate_repository(".")
    print(f"Status:      {res2.get('status')}")
    print(f"Repo Name:   {res2.get('repo_name')}")
    print(f"Tech Stack:  {res2.get('tech_stack')}")
    print(f"Key Files:   {res2.get('key_files')[:8]}")
    assert res2.get("status") == "success"

    # -------------------------------------------------------------------
    # TEST 3: Git Status Inspection
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 3: Git Status Inspection")
    print("-" * 60)
    res3 = integrator.get_repo_status(".")
    print(f"Status:      {res3.get('status')}")
    print(f"Branch:      {res3.get('branch')}")
    print(f"Commit:      {res3.get('latest_commit')}")
    assert res3.get("status") == "success"

    # -------------------------------------------------------------------
    # TEST 4: Execute CLI Command via Hands
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 4: Execute Terminal CLI Command")
    print("-" * 60)
    res4 = org.hands.act("run_command", {"command": "git --version"})
    print(f"Tool:        {res4.get('tool')}")
    print(f"Status:      {res4.get('status')}")
    print(f"Result:      {res4.get('result')}")
    assert res4.get("status") == "success"

    print("\n" + "=" * 70)
    print("   ALL REPOSITORY INTEGRATION TESTS PASSED [OK]")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
