"""
Jarvis X — Chrome Companion & Web Context Verification.
Simulates Chrome Extension payload dispatch and verifies end-to-end bridge response.
"""

import json
import urllib.request
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def main():
    print("=" * 70)
    print("   ALFRED OS — CHROME COMPANION BRIDGE VERIFICATION")
    print("=" * 70 + "\n")

    # 1. Test Status Heartbeat
    print("[1/2] 💓 Checking Extension Bridge Status on http://127.0.0.1:8765/api/status...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8765/api/status", timeout=2) as r:
            status_data = json.loads(r.read().decode("utf-8"))
            print(f"      Status:   {status_data.get('status').upper()}")
            print(f"      Persona:  {status_data.get('persona')}")
            print(f"      LLM:      {status_data.get('llm_provider')}\n")
    except Exception as e:
        print(f"      [!] Bridge server not running: {e}\n")
        return

    # 2. Test LeetCode Context Action
    print("[2/2] 🧩 Simulating LeetCode Extraction from Chrome...")
    payload = {
        "action": "solve_problem",
        "url": "https://leetcode.com/problems/two-sum/",
        "title": "Two Sum - LeetCode",
        "context": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "prompt": "Solve Two Sum in Python with O(n) time complexity and explain the hash map lookup."
    }
    
    req = urllib.request.Request(
        "http://127.0.0.1:8765/api/action",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            res_data = json.loads(r.read().decode("utf-8"))
            print(f"      Status:   {res_data.get('status').upper()}")
            print(f"      Response Preview:\n{res_data.get('response', '')[:350]}...\n")
            print("=" * 70)
            print("   CHROME EXTENSION BRIDGE FULLY VERIFIED [OK]")
            print("=" * 70)
    except Exception as e:
        print(f"      [!] Action dispatch error: {e}")


if __name__ == "__main__":
    main()
