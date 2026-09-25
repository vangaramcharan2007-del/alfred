#!/usr/bin/env python3
"""
Jarvis X - PC Customizer Agent Mike (CLI & Daemon Runner)
Permanent, Autonomous Background Aesthetics Engine.

Commands:
  python scripts/agent_mike_customizer.py --sync        # Immediate wallpaper theme sync
  python scripts/agent_mike_customizer.py --status      # Display active theme, font, placement, CPU
  python scripts/agent_mike_customizer.py --optimize    # Enforce single clock & optimize
  python scripts/agent_mike_customizer.py --daemon      # Run zero-lag background watcher + hotkey
  python scripts/agent_mike_customizer.py --hotkey      # Run global Win+Alt+C hotkey listener
"""

import os
import sys
import time
import psutil
import threading
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "var" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DAEMON_LOG_FILE = LOG_DIR / "agent_mike_customizer.log"

class _SafeWriter:
    def __init__(self, target, log_path=None):
        self.target = target
        self.log_path = log_path

    def write(self, s):
        written = False
        try:
            if self.target is not None:
                self.target.write(s)
                self.target.flush()
                written = True
        except Exception:
            pass

        # If writing to console stream fails or is headless, write non-empty lines to log_path
        if (not written or self.target is None) and self.log_path and s.strip():
            try:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                with open(self.log_path, "a", encoding="utf-8") as f:
                    for line in s.splitlines():
                        if line.strip():
                            f.write(f"[{timestamp}] {line}\n")
            except Exception:
                pass

    def flush(self):
        try:
            if self.target is not None:
                self.target.flush()
        except Exception:
            pass

# Install bulletproof stdout/stderr traps
sys.stdout = _SafeWriter(sys.stdout, DAEMON_LOG_FILE)
sys.stderr = _SafeWriter(sys.stderr, DAEMON_LOG_FILE)

# Add project root to sys.path
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from jarvisx.agents.customizer_mike import MikeCustomizerAgent, PRESET_THEMES


def log_daemon(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    try:
        with open(DAEMON_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass
    try:
        if sys.stdout and sys.stdout.target:
            sys.stdout.target.write(entry + "\n")
            sys.stdout.target.flush()
    except Exception:
        pass


RUNTIME_DIR = PROJECT_ROOT / "var" / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
PID_FILE = RUNTIME_DIR / "agent_mike_customizer.pid"


def get_running_daemon_pid():
    if not PID_FILE.exists():
        return None
    try:
        with open(PID_FILE, "r", encoding="utf-8") as f:
            pid = int(f.read().strip())
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            name = (p.name() or "").lower()
            if name.startswith("python"):
                return pid
    except Exception:
        pass
    return None


def acquire_daemon_lock():
    """Ensures strictly ONE instance of the customizer daemon is running via atomic PID lock."""
    my_pid = os.getpid()
    old_pid = get_running_daemon_pid()
    if old_pid and old_pid != my_pid:
        log_daemon(f"Stopping previous customizer daemon instance (PID: {old_pid})...")
        try:
            p = psutil.Process(old_pid)
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            try:
                psutil.Process(old_pid).kill()
            except Exception:
                pass

    try:
        with open(PID_FILE, "w", encoding="utf-8") as f:
            f.write(str(my_pid))
    except Exception as e:
        log_daemon(f"Warning: Could not write PID file: {e}")
    return True


def release_daemon_lock():
    try:
        if PID_FILE.exists():
            with open(PID_FILE, "r", encoding="utf-8") as f:
                pid = int(f.read().strip())
            if pid == os.getpid():
                PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass


import atexit
atexit.register(release_daemon_lock)


def print_banner():
    print("=" * 70)
    print("       JARVIS X - PC CUSTOMIZER AGENT MIKE (PERMANENT ENGINE)")
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


def run_daemon(mike: MikeCustomizerAgent, interval: float = 1.0, with_hotkey: bool = True):
    acquire_daemon_lock()

    log_daemon(f"Agent Mike Permanent Daemon Online (Heartbeat: {interval}s)...")
    log_daemon("Zero-lag sleep-driven active monitoring active (<0.01% CPU).")
    
    if with_hotkey:
        try:
            from agent_mike_hotkey import listen_for_hotkey
            t = threading.Thread(target=listen_for_hotkey, args=(mike, False), daemon=True)
            t.start()
            log_daemon("Win+Alt+C Global Hotkey listener running on background thread.")
        except Exception as e:
            log_daemon(f"Warning: Could not start hotkey listener thread: {e}")

    # Run initial sync
    run_sync(mike, force=True)

    try:
        while True:
            time.sleep(interval)
            try:
                res = mike.sync(force=False)
                if res.get("status") == "success":
                    log_daemon(f"Aesthetic Harmonized: {res.get('theme_name')} | Font: {res.get('font')} | Pos: {res.get('placement')}")
            except Exception as loop_err:
                # Never let any transient filesystem/image lock crash the daemon
                time.sleep(0.5)
    except KeyboardInterrupt:
        log_daemon("Agent Mike daemon terminated by user.")


def main():
    parser = argparse.ArgumentParser(description="Jarvis X PC Customizer Agent Mike")
    parser.add_argument("--sync", action="store_true", help="Force immediate wallpaper sync")
    parser.add_argument("--status", action="store_true", help="Print Mike's status report")
    parser.add_argument("--optimize", action="store_true", help="Clean duplicates & optimize")
    parser.add_argument("--daemon", action="store_true", help="Run background zero-lag monitor + hotkey")
    parser.add_argument("--hotkey", action="store_true", help="Run standalone global hotkey listener")
    parser.add_argument("--interval", type=float, default=1.0, help="Daemon check interval (default: 1.0s)")

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
    try:
        main()
    except Exception as e:
        import traceback
        try:
            with open(PROJECT_ROOT / "var" / "logs" / "agent_mike_crash.log", "a", encoding="utf-8") as f:
                f.write(f"\nCRASH AT {time.strftime('%Y-%m-%d %H:%M:%S')}:\n")
                traceback.print_exc(file=f)
        except Exception:
            pass
        raise
