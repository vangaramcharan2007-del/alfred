"""
Live Verification: Autonomous LLM Feature Assimilation & Architectural Synthesizer.
"""

import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvisx.organism import get_organism
from jarvisx.engineering.autonomous_feature_assimilator import get_feature_assimilator

async def main():
    print("=" * 70)
    print("   ALFRED OS — AUTONOMOUS LLM FEATURE ASSIMILATION & SYNTHESIZER")
    print("=" * 70 + "\n")

    assimilator = get_feature_assimilator()
    org = get_organism()

    # -------------------------------------------------------------------
    # TEST 1: User's Natural Prompt via Living Organism
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 1: LLM Architectural Brain Understanding")
    print("-" * 60)
    prompt = "the agent should know what is needed and what is not to our project that means it should think and add the features automatically using llm"
    res1 = await org.react_turn(prompt)
    print(f"Decision: {res1.get('decision')}")
    print(f"Spoken/Response:\n{res1.get('response') or res1.get('spoken')}\n")

    # -------------------------------------------------------------------
    # TEST 2: Autonomous LLM Feature Assimilation on Real Repo
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 2: End-to-End Autonomous Assimilation of a DSA Repo")
    print("-" * 60)
    res2 = assimilator.assimilate_feature_from_repo(
        repo_url="https://github.com/octocat/Hello-World",
        feature_goal="Create a clean, typed system greeting utility with latency telemetry for Alfred OS",
        target_module_name="system_telemetry_greeter.py"
    )
    print(f"Status:          {res2.get('status')}")
    print(f"Module Created:  {res2.get('module_created')}")
    print(f"Test Created:    {res2.get('test_created')}")
    print(f"Rationale:       {res2.get('rationale')}")
    print(f"Bloat Discarded: {res2.get('bloat_discarded')}")
    print(f"Features Kept:   {res2.get('features_retained')}")
    print(f"Verification:    {res2.get('verification')}")
    assert res2.get("status") == "success"
    assert os.path.exists("src/jarvisx/integrations/system_telemetry_greeter.py")

    print("\n" + "=" * 70)
    print("   ALL AUTONOMOUS FEATURE ASSIMILATION TESTS PASSED [OK]")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
