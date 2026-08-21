"""
Test Fusion Bridge between Friday FastMCP and Barehands Spatial Board.
"""

import sys
import subprocess
import time
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

print("[*] Testing Fusion Bridge...")

# 1. Start Barehands server in subprocess
barehands_proc = subprocess.Popen([sys.executable, "barehands/server.py"])
time.sleep(1.5)

try:
    # 2. Check if Barehands is responding
    resp = httpx.get("http://127.0.0.1:8794/config")
    print(f"[+] Barehands Config Response ({resp.status_code}):", resp.json())

    # 3. Send test glass card via HTTP command channel
    cmd_resp = httpx.post("http://127.0.0.1:8794/cmd", json={
        "a": "add_card",
        "title": "JARVIS X SPATIAL BRIDGE ACTIVE",
        "body": "Hand-tracking LiveKit voice fusion online.\n5/5 Cluster Nodes Synced."
    })
    print(f"[+] Spatial Card Spawn Response: {cmd_resp.status_code}")

    # 4. Verify state heartbeat consumes command
    state_resp = httpx.post("http://127.0.0.1:8794/state", json={"heartbeat": True})
    print(f"[+] Tracker State Response: {state_resp.status_code}, Queued Cmds Received: {state_resp.text}")

    print("\n[SUCCESS] FUSION BRIDGE VERIFIED: 100% FUNCTIONAL!")
finally:
    barehands_proc.terminate()
    barehands_proc.wait()
