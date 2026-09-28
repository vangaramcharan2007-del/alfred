#!/usr/bin/env python3
"""
Jarvis X - RDR2 Sentinel Daemon CLI Runner
Spawns and manages the autonomous RDR2 Performance & Thermal Sentinel.

Usage:
  python scripts/rdr2_sentinel_daemon.py --start       # Start in foreground (interactive log)
  python scripts/rdr2_sentinel_daemon.py --daemon      # Spawn headless background watchdog (pythonw)
  python scripts/rdr2_sentinel_daemon.py --status      # Check if Sentinel is alive and healthy
  python scripts/rdr2_sentinel_daemon.py --stop        # Gracefully stop running Sentinel
  python scripts/rdr2_sentinel_daemon.py --calibrate   # Apply 50-60 FPS Golden Frontier settings
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

LOG_FILE = PROJECT_ROOT / "logs" / "rdr2_sentinel.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


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


sys.stdout = _SafeWriter(sys.stdout, LOG_FILE)
sys.stderr = _SafeWriter(sys.stderr, LOG_FILE)

from jarvisx.agents.rdr2_sentinel import RDR2PerformanceSentinel



PID_FILE = PROJECT_ROOT / "var" / "runtime" / "rdr2_sentinel.pid"
PID_FILE.parent.mkdir(parents=True, exist_ok=True)


def get_sentinel_pids():
    import psutil
    pids = []

    # 1. Check PID file first
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)
                if p.is_running() and p.status() != psutil.STATUS_ZOMBIE:
                    pids.append(pid)
                    return pids
            # Stale PID file
            try:
                PID_FILE.unlink(missing_ok=True)
            except Exception:
                pass
        except Exception:
            pass

    # 2. Fallback: inspect process table
    current_pid = os.getpid()
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if p.info["pid"] == current_pid:
                continue
            cmd = " ".join(p.info.get("cmdline") or []).lower()
            if "rdr2_sentinel" in cmd and "--start" in cmd and "--daemon" not in cmd and "--status" not in cmd:
                pids.append(p.info["pid"])
        except Exception:
            pass
    return pids


def start_foreground():
    import atexit
    current_pid = os.getpid()
    PID_FILE.write_text(str(current_pid), encoding="utf-8")

    def _cleanup_pid():
        try:
            if PID_FILE.exists():
                PID_FILE.unlink(missing_ok=True)
        except Exception:
            pass

    atexit.register(_cleanup_pid)

    try:
        sentinel = RDR2PerformanceSentinel()
        cal = sentinel.calibrate_60fps_golden_preset()
        print(f"[+] Graphics Preset Configured: {cal.get('target_fps', '50-60 FPS')}")
        print(f"    Textures: {cal.get('textures')} | FSR 2.0: {cal.get('fsr2')} | Shadows: {cal.get('shadows')}")
        sentinel.start_sentinel_daemon()
    finally:
        _cleanup_pid()


def start_daemon():
    pids = get_sentinel_pids()
    if pids:
        print(f"[!] RDR2 Sentinel is already running in background (PID(s): {pids}).")
        return

    # Calibrate preset
    sentinel = RDR2PerformanceSentinel()
    cal = sentinel.calibrate_60fps_golden_preset()
    print(f"[+] 50-60 FPS Preset Loaded: {cal.get('target_fps')}")

    # Launch headless via pythonw with full detachment
    pythonw = Path(sys.executable).parent / "pythonw.exe"
    runner_py = str(Path(__file__).resolve())
    cmd = [str(pythonw), runner_py, "--start"]

    # DETACHED_PROCESS (0x8) | CREATE_NEW_PROCESS_GROUP (0x200)
    flags = 0x00000008 | 0x00000200
    proc = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        creationflags=flags,
        close_fds=True
    )
    time.sleep(1.0)
    print(f"[OK] RDR2 Performance & Thermal Sentinel spawned in background (PID: {proc.pid}).")
    print(f"     Log: {sentinel.log_file}")


def check_status():
    pids = get_sentinel_pids()
    sentinel = RDR2PerformanceSentinel()
    envelope = sentinel.read_system_envelope()

    print("=" * 68)
    print("  [SENTINEL] JARVIS X - RDR2 PERFORMANCE & THERMAL SENTINEL STATUS")
    print("=" * 68)
    if pids:
        print(f"  [+] Daemon Status        : ACTIVE / MONITORING (PID(s): {pids})")
    else:
        print(f"  [-] Daemon Status        : INACTIVE / STANDBY")
    print(f"  [+] Active RDR2 Game     : {'YES (Under Sentinel Guard)' if envelope.get('game_active') else 'NO (Awaiting Launch)'}")
    print(f"  [+] Available Memory     : {envelope.get('ram_available_gb')} GB ({envelope.get('ram_used_pct')}% used)")
    print(f"  [+] CPU Frequency        : {envelope.get('cpu_freq_mhz')} MHz (Meteor Lake Unthrottled)")
    print(f"  [+] Log File Path        : {sentinel.log_file}")
    print("=" * 68 + "\n")



def stop_sentinel():
    import psutil
    pids = get_sentinel_pids()
    if not pids:
        print("[-] No running RDR2 Sentinel daemon found.")
        return

    for pid in pids:
        try:
            p = psutil.Process(pid)
            p.terminate()
            print(f"[+] Terminated Sentinel process {pid}.")
        except Exception as e:
            print(f"[-] Could not terminate {pid}: {e}")
    print("[✔] RDR2 Sentinel stopped.")


def main():
    import traceback
    try:
        parser = argparse.ArgumentParser(description="RDR2 Performance Sentinel CLI")
        parser.add_argument("--start", action="store_true", help="Start sentinel in foreground")
        parser.add_argument("--daemon", action="store_true", help="Start sentinel in background (headless)")
        parser.add_argument("--status", action="store_true", help="Check sentinel daemon status")
        parser.add_argument("--stop", action="store_true", help="Stop running sentinel daemon")
        parser.add_argument("--calibrate", action="store_true", help="Calibrate 50-60 FPS graphics preset")

        args = parser.parse_args()

        if args.calibrate:
            s = RDR2PerformanceSentinel()
            res = s.calibrate_60fps_golden_preset()
            print(f"[+] Calibrated 50-60 FPS Profile: {res}")
        elif args.daemon:
            start_daemon()
        elif args.status:
            check_status()
        elif args.stop:
            stop_sentinel()
        else:
            # Default foreground/worker start
            start_foreground()
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[CRASH] {time.strftime('%Y-%m-%d %H:%M:%S')} Top-level exception: {e}\n")
            f.write(traceback.format_exc() + "\n")
        raise


if __name__ == "__main__":
    main()

