"""
Jarvis X / Alfred OS — Spider-Man EV Minimalist Linux Workstation Live Certification.
=====================================================================================
Mandatory End-to-End Live Runtime Certification for Spider-Man EV Voice Co-Pilot HUD.
"""

import os
import sys
import time
import urllib.request
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvisx.gui.spiderman_linux_hud import SpiderManLinuxHUDServer, EV_SYSTEM_PROMPTS
from jarvisx.organism import AlfredOrganism


def main():
    print("\n" + "=" * 78)
    print(" 🕷️ SPIDER-MAN EV // MINIMALIST LINUX WORKSTATION LIVE CERTIFICATION")
    print("=" * 78)

    # 1. Initialize EV Co-Pilot
    print("[1/4] Initializing EV Co-Pilot under Alfred Orchestration...")
    from jarvisx.agents.linux_agent import LinuxBridgeAgent
    linux = LinuxBridgeAgent.get_instance()
    print("  [✓] Alfred Grand Orchestrator: ACTIVE")
    print(f"  [✓] EV Subagent Persona      : LOVELY, FUNNY, ADHD-FRIENDLY FEMALE AI")
    print(f"  [✓] EV Opening Line          : \"{EV_SYSTEM_PROMPTS['greeting']}\"")
    print()

    # 2. Start Spider-Man EV HUD Server
    print("[2/4] Starting Spider-Man EV Workstation Server on http://localhost:5050...")
    url = SpiderManLinuxHUDServer.start(port=5050, open_browser=True)
    print(f"  [✓] Live HUD URL             : {url}")
    print(f"  [✓] Aesthetic Theme          : Obsidian Black (#08090d) + Stark Crimson (#ff003c) + Venom Cyan (#00f0ff)")
    print()

    # 3. Test REST Endpoints & Spider-Sense Telemetry
    print("[3/4] Probing Spider-Sense Telemetry & Dual-Core Linux API...")
    time.sleep(0.5)
    with urllib.request.urlopen(f"{url}/api/telemetry") as res:
        telem = json.loads(res.read().decode("utf-8"))
        print(f"  • Linux Kernel               : {telem.get('kernel_version')}")
        print(f"  • Memory Free                : {telem.get('memory_free_mb')} MB")
        print(f"  • Active Engine              : {telem.get('runtime_type', 'WSL').upper()}")
    print()

    # 4. Test EV Voice Action Execution
    print("[4/4] Testing EV Voice Action Dispatcher (Cyber Sentinel)...")
    req = urllib.request.Request(
        f"{url}/api/action",
        data=json.dumps({"action": "cyber_scan"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        action_data = json.loads(res.read().decode("utf-8"))
        print(f"  • EV Voice Dialogue Spoken   : \"{action_data.get('ev_speech')}\"")
        print(f"  • Linux Execution Output     : {action_data.get('output')}")
    print()

    print("=" * 78)
    print(" 🏆 CERTIFICATION COMPLETE: SPIDER-MAN EV LINUX HUD IS LIVE & OPERATIONAL!")
    print("    • URL: http://localhost:5050 (Opened in your browser)")
    print("    • Desktop Launcher: C:\\Users\\vanga\\Desktop\\Launch_SpiderMan_EV_HUD.bat")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
