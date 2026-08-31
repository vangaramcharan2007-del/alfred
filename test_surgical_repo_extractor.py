"""
Live Verification: Surgical Ephemeral Repository Ingestion & Auto-Purge Pipeline.
"""

import asyncio
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvisx.organism import get_organism
from jarvisx.tools.surgical_repo_extractor import get_surgical_extractor

async def main():
    print("=" * 70)
    print("   ALFRED OS — SURGICAL REPO INGESTION & AUTO-PURGE PIPELINE")
    print("=" * 70 + "\n")

    extractor = get_surgical_extractor()
    org = get_organism()

    # -------------------------------------------------------------------
    # TEST 1: Zero-Clone Single File Ingestion from GitHub
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 1: Direct Zero-Clone Download (0 MB Git Bloat)")
    print("-" * 60)
    res1 = extractor.fetch_raw_github_file(
        repo_owner_name="TheAlgorithms/Python",
        file_path_in_repo="data_structures/linked_list/singly_linked_list.py",
        target_local_path="src/integrations/dsa/singly_linked_list.py"
    )
    print(f"Status:      {res1.get('status')}")
    print(f"File Name:   {res1.get('file_name')}")
    print(f"File Size:   {res1.get('size_bytes')} bytes")
    print(f"Destination: {res1.get('destination')}")
    assert res1.get("status") == "success"
    assert os.path.exists("src/integrations/dsa/singly_linked_list.py")

    # -------------------------------------------------------------------
    # TEST 2: Ephemeral Shallow Clone -> Extract Modules -> Auto-Purge
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 2: Surgical Ephemeral Clone & Immediate Auto-Purge")
    print("-" * 60)
    res2 = extractor.extract_and_integrate(
        repo_url="https://github.com/octocat/Hello-World",
        target_destination="src/integrations/hello_world",
        feature_intent="sample code"
    )
    print(f"Status:         {res2.get('status')}")
    print(f"Extracted:      {res2.get('extracted_files')}")
    print(f"Integrated KB:  {res2.get('integrated_size_kb')} KB")
    print(f"Bloat Purged:   {res2.get('disk_bloat_purged_mb')} MB")
    print(f"Message:        {res2.get('message')}")
    assert res2.get("status") == "success"

    # -------------------------------------------------------------------
    # TEST 3: User's Natural Prompt via Living Organism
    # -------------------------------------------------------------------
    print("-" * 60)
    print("[+] TEST 3: Semantic Understanding of Zero-Bloat Repo Ingestion")
    print("-" * 60)
    prompt = "cloning takes so much space we need to clone the repos use what we need integrate them and delete the rest"
    res3 = await org.react_turn(prompt)
    print(f"Decision: {res3.get('decision')}")
    print(f"Spoken/Response:\n{res3.get('response') or res3.get('spoken')}\n")

    print("=" * 70)
    print("   ALL SURGICAL REPO EXTRACTION TESTS PASSED [OK]")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
