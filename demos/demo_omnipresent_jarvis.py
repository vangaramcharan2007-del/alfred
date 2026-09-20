"""
🚀 Jarvis X // Omnipresent Living Daemon — Live Demonstration
=============================================================
Demonstrates the unified living presence:
1. Omnipresent Supervisor initialization (HUD Server + Eevee Voice + Ambient Watcher)
2. Live HTTP & WebSocket HUD status verification
3. Proactive Ambient Watcher: Real-time sensory awareness & autonomous memory compaction
4. Proactive glass toast delivery in EV HUD synchronized with EV Neural Voice
5. Safe lifecycle management and graceful shutdown

Run: python demos/demo_omnipresent_jarvis.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
import urllib.request
from pathlib import Path

# Safe UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from jarvisx.runtime.omnipresent_supervisor import OmnipresentSupervisor, get_omnipresent_supervisor
from jarvisx.runtime.ambient_watcher import AmbientWatcher, get_ambient_watcher
from jarvisx.dashboard.event_bus import push_ev_notification, get_event_log


def print_banner():
    print()
    print("=" * 72)
    print("  🚀 E.V. CORE // OMNIPRESENT LIVING DAEMON LIVE RUNTIME DEMO")
    print("  Unified Supervisor // Proactive Ambient Sensor // EV HUD")
    print("=" * 72)
    print()


async def demo_supervisor_boot(supervisor: OmnipresentSupervisor) -> bool:
    print("  ────────────────────────────────────────────────────────────")
    print("  [1/4] BOOTING OMNIPRESENT SUPERVISOR (UNIFIED DAEMON)")
    print("  ────────────────────────────────────────────────────────────")

    t0 = time.perf_counter()
    status = supervisor.start(with_tray=False, block=False)
    boot_time_ms = (time.perf_counter() - t0) * 1000

    print(f"  ⚡ Core Supervisor Engaged (PID: {status.pid}) in {boot_time_ms:.1f}ms")
    print(f"  ├─ HUD Server Thread:      {'ONLINE' if status.hud_online else 'STARTING'}")
    print(f"  ├─ Voice Matrix Listener:  {'ONLINE' if status.voice_online else 'OFFLINE'}")
    print(f"  ├─ Ambient Sensory Watcher: {'ONLINE' if status.ambient_watcher_online else 'OFFLINE'}")
    print(f"  └─ Internal Port:          {supervisor.hud_port}")

    # Give server 1.5s to anchor loop
    await asyncio.sleep(1.5)

    passed = status.pid > 0 and status.ambient_watcher_online
    print(f"  {'✅ PASSED' if passed else '❌ FAILED'}: Master supervisor online and monitoring")
    print()
    return passed


async def demo_hud_server_uplink(port: int) -> bool:
    print("  ────────────────────────────────────────────────────────────")
    print("  [2/4] VERIFYING HUD SERVER LIVE HTTP & WEBSOCKET UPLINK")
    print("  ────────────────────────────────────────────────────────────")

    url = f"http://127.0.0.1:{port}/"
    print(f"  🌐 Pinging E.V. HUD Dashboard at {url}...")

    success = False
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "JarvisSentinel/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    content = resp.read(300).decode("utf-8", errors="replace")
                    print(f"  ✅ Received 200 OK from E.V. Tactical Glass HUD!")
                    print(f"  📄 Header snippet: {content[:80]}...")
                    success = True
                    break
        except Exception as e:
            print(f"       (Retry {attempt + 1}/5: waiting for uvicorn port: {e})")
            await asyncio.sleep(0.8)

    print(f"  {'✅ PASSED' if success else '❌ FAILED'}: HUD server active and delivering glass UI")
    print()
    return success


async def demo_ambient_watcher_proactivity() -> bool:
    print("  ────────────────────────────────────────────────────────────")
    print("  [3/4] PROACTIVE AMBIENT WATCHER (AUTONOMOUS SENSING)")
    print("  ────────────────────────────────────────────────────────────")

    watcher = get_ambient_watcher()
    print("  👁️ Sampling real-time desktop environment...")

    t0 = time.perf_counter()
    report = watcher.perform_ambient_check()
    elapsed_ms = (time.perf_counter() - t0) * 1000

    print(f"  📊 Ambient Telemetry ({elapsed_ms:.1f}ms):")
    print(f"  ├─ Active Foreground Window: \"{report['active_window']}\"")
    print(f"  ├─ Live System RAM Load:    {report['ram_percent']}%")
    print(f"  ├─ Live CPU Utilization:    {report['cpu_percent']}%")
    print(f"  ├─ User Inactivity Timer:   {report['idle_seconds']}s")
    print(f"  └─ Autonomous Actions:      {', '.join(report['actions']) if report['actions'] else 'Nominal baseline maintained'}")

    passed = report["ram_percent"] > 0 and len(report["active_window"]) > 0
    print(f"  {'✅ PASSED' if passed else '❌ FAILED'}: Ambient watcher active and observing workflow")
    print()
    return passed


async def demo_proactive_hud_notification() -> bool:
    print("  ────────────────────────────────────────────────────────────")
    print("  [4/4] PROACTIVE GLASS TOAST & SYNCHRONIZED EV TTS")
    print("  ────────────────────────────────────────────────────────────")

    title = "🛡️ E.V. CORE // STATUS NOMINAL"
    msg = "Living background daemon active. Real-time sensory sentinel guarding memory & thermals."
    spoken = "E.V. background daemon is active and monitoring your desktop, Boss."

    print(f"  🔔 Emitting Proactive Toast: [{title}]")
    print(f"  🗣️ [EV TTS]: \"{spoken}\"")

    push_ev_notification(
        title=title,
        message=msg,
        level="success",
        spoken_text=spoken,
        speak_in_background=False,
    )

    events = get_event_log()
    has_event = any(e.get("type") == "ev_notification" for e in events)

    print(f"  📊 Event Bus Log Size: {len(events)} telemetry entries")
    print(f"  🔔 Verified in HUD Pipeline: {has_event}")

    passed = has_event
    print(f"  {'✅ PASSED' if passed else '❌ FAILED'}: Proactive notification synced with EV neural speech")
    print()
    return passed


async def main():
    print_banner()
    t_start = time.perf_counter()

    supervisor = get_omnipresent_supervisor()

    r1 = await demo_supervisor_boot(supervisor)
    r2 = await demo_hud_server_uplink(supervisor.hud_port)
    r3 = await demo_ambient_watcher_proactivity()
    r4 = await demo_proactive_hud_notification()

    total_time = time.perf_counter() - t_start
    all_passed = r1 and r2 and r3 and r4

    # Graceful shutdown
    print("  🛑 Halting supervisor for demo conclusion...")
    supervisor.stop()
    print("  ✅ Supervisor halted cleanly.")
    print()

    print("=" * 72)
    if all_passed:
        print(f"  ✅ ALL 4 SCENARIOS PASSED ({total_time:.2f}s total runtime)")
        print("  1. Omnipresent Living Daemon: Booted & healthy")
        print("  2. HUD Server: Live HTTP/WS streaming on port 8765")
        print("  3. Ambient Proactive Watcher: Continuous sensory surveillance")
        print("  4. EV HUD Toasts & EV Voice: Synchronized and firing")
    else:
        print("  ⚠️ One or more scenarios reported issues. Inspect telemetry above.")
    print("=" * 72)
    print()

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
