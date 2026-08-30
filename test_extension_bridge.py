"""
Test suite to verify the Alfred Chrome Extension Bridge Server and API Endpoints.
"""

import json
import os
import sys
import time
import urllib.request

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvisx.runtime.extension_server import start_extension_server, ExtensionBridgeServer

def main():
    print("=" * 70)
    print("TEST: Starting Alfred Chrome Extension Bridge Server")
    print("=" * 70)

    server = start_extension_server()
    assert server.running, "Extension bridge server should be running!"
    time.sleep(0.5)

    print("\n[+] TEST 1: GET /api/status endpoint")
    req = urllib.request.Request("http://127.0.0.1:8765/api/status")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        print(f"Status Response: {data}")
        assert data.get("status") == "online"

    print("\n[+] TEST 2: POST /api/action endpoint (Simulating Chrome Extension)")
    post_payload = {
        "action": "chat",
        "prompt": "What is the time complexity of QuickSort?",
        "title": "Sorting Algorithms",
        "url": "https://en.wikipedia.org/wiki/Quicksort"
    }
    req2 = urllib.request.Request(
        "http://127.0.0.1:8765/api/action",
        data=json.dumps(post_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req2) as resp2:
        assert resp2.status == 200, f"Expected 200, got {resp2.status}"
        data2 = json.loads(resp2.read().decode("utf-8"))
        print(f"Action Status: {data2.get('status')}")
        print(f"Response snippet:\n{data2.get('response')[:300]}...\n")
        assert data2.get("status") == "success"

    print("=" * 70)
    print("ALL CHROME EXTENSION BRIDGE TESTS PASSED [OK]")
    print("=" * 70)

if __name__ == "__main__":
    main()
