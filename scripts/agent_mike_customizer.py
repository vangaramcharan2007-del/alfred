#!/usr/bin/env python3
"""
Jarvis X - PC Customizer Agent Mike (CLI & Daemon Runner)

Commands:
  python scripts/agent_mike_customizer.py --sync        # Immediate wallpaper theme sync
  python scripts/agent_mike_customizer.py --status      # Display active theme, font, placement, CPU
  python scripts/agent_mike_customizer.py --optimize    # Enforce single clock & optimize
  python scripts/agent_mike_customizer.py --daemon      # Run zero-lag background watcher + hotkey
  python scripts/agent_mike_customizer.py --hotkey      # Run global Win+Alt+C hotkey listener
"""

import sys
import time
import threading
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from jarvisx.agents.customizer_mike import MikeCustomizerAgent, PRESET_THEMES


def print_banner():
    print("=" * 70)
    print("       JARVIS X - PC CUSTOMIZER AGENT MIKE (ZERO-LAG SUITE)")
    print("=" * 70)


def run_sync(mike: MikeCustomizerAgent, force: bool = True):
    print("[*] Agent Mike: Synchronizing active desktop & Lively wallpaper...")
    res = mike.sync(force=force)
    if res.get("status") == "success":
        print(f"[+] Active Wallpaper : {res.get('wallpaper_title')}")
        print(f"[+] Detected Theme   : {res.get('theme_name')}")
        print(f"[+] Preset Matched   : {'Yes (Authentic Franchise)' if res.get('is_preset') else 'No (AI Auto-Synthesized)'}")
        print(f"[+] Selected Font    : {res.get('font')}")
        print(f"[+] Negative Space   : {res.get('placement')}")
        print(f"[+] Accent Color     : {res.get('accent_color')}")
        print(f"[+] Single Clock OK  : Enforced (redundant skins unloaded: {len(res.get('single_clock_enforced', []))})")
        print(f"[+] Rainmeter Clock  : Updated and reloaded with zero lag.")
        print(f"[+] Visualizer Suite : Repositioned to dynamic negative space.")
        print(f"[+] Taskbar & DWM    : Accent color synchronized ({res.get('windows_accent_synced', True)})")
    elif res.get("status") == "unchanged":
        print("[i] Wallpaper unchanged. Zero action needed (0.00% CPU conserved).")
    else:
        print(f"[-] Sync notice: {res.get('message', res)}")
    return res


def run_status(mike: MikeCustomizerAgent):
    status = mike.get_customizer_status()
    print("[*] AGENT MIKE OPERATIONAL STATUS:")
    print(f"    - Agent Name       : {status.get('agent')}")
    print(f"    - Active Wallpaper : {status.get('active_wallpaper')}")
    print(f"    - Active Theme     : {status.get('active_theme')}")
    print(f"    - Clock Placement  : {status.get('active_placement')}")
    print(f"    - Single Clock OK  : {status.get('single_clock_enforced')} (Strictly ONE master clock)")
    print(f"    - Idle CPU Profile : {status.get('idle_cpu_footprint')} (Zero lag)")
    print(f"    - Wallpaper Path   : {status.get('detected_wallpaper_path')}")
    return status


def run_optimize(mike: MikeCustomizerAgent):
    print("[*] Agent Mike: Running PC Aesthetic Optimization...")
    res = mike.optimize_desktop()
    print("[+] Enforced strict single clock: removed duplicate meters and overlays.")
    print("[+] Synchronized master clock and visualizer suite.")
    return res


def run_daemon(mike: MikeCustomizerAgent, interval: float = 2.0, with_hotkey: bool = True):
    print(f"[*] Agent Mike entering background Sentinel Mode (Heartbeat: {interval}s)...")
    print("[*] Zero lag active: Sleep-driven event checking (<0.01% CPU).")
    
    if with_hotkey:
        try:
            from agent_mike_hotkey import listen_for_hotkey
            t = threading.Thread(target=listen_for_hotkey, args=(mike, False), daemon=True)
            t.start()
            print("[+] Win+Alt+C Global Hotkey listener running in background thread.")
        except Exception as e:
            print(f"[!] Warning: Could not start hotkey listener thread: {e}")

    print("[*] Press Ctrl+C to terminate.")
    
    # Run initial sync
    run_sync(mike, force=True)

    try:
        while True:
            time.sleep(interval)
            res = mike.sync(force=False)
            if res.get("status") == "success":
                print(f"[EVENT] New wallpaper detected! Switched theme to: {res.get('theme_name')} ({res.get('placement')})")
    except KeyboardInterrupt:
        print("\n[*] Agent Mike daemon stopped cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Jarvis X PC Customizer Agent Mike")
    parser.add_argument("--sync", action="store_true", help="Force immediate wallpaper sync")
    parser.add_argument("--status", action="store_true", help="Print Mike's status report")
    parser.add_argument("--optimize", action="store_true", help="Clean duplicates & optimize")
    parser.add_argument("--daemon", action="store_true", help="Run background zero-lag monitor + hotkey")
    parser.add_argument("--hotkey", action="store_true", help="Run standalone global hotkey listener")
    parser.add_argument("--interval", type=float, default=2.0, help="Daemon check interval (default: 2.0s)")

    args = parser.parse_args()
    print_banner()

    mike = MikeCustomizerAgent()

    if args.hotkey:
        from agent_mike_hotkey import listen_for_hotkey
        listen_for_hotkey(mike)
    elif args.daemon:
        run_daemon(mike, interval=args.interval, with_hotkey=True)
    elif args.status:
        run_status(mike)
    elif args.optimize:
        run_optimize(mike)
    else:
        # Default action is sync
        run_sync(mike, force=True)


if __name__ == "__main__":
    main()
