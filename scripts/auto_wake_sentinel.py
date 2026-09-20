"""
Auto-Wake Sentinel for Naruto 4K Live Lock Screen.
==================================================
Runs silently in the background (zero CPU footprint).
Detects whenever the laptop lid is opened / PC resumes from sleep,
and automatically launches the Naruto 4K Live Wallpaper Lock Screen.
"""

import os
import sys
import time
import subprocess
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAUNCH_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "launch_now.py")
LOCK_PROFILE = os.path.join(tempfile.gettempdir(), "naruto_lock_runtime_profile")
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
HTML_PATH = os.path.join(PROJECT_ROOT, "src", "jarvisx", "gui", "naruto_lockscreen.html")


def is_lockscreen_open() -> bool:
    """Check if the lockscreen is already active."""
    try:
        cmd = ["powershell", "-Command", "Get-Process msedge -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like '*Naruto*' -or $_.CommandLine -like '*naruto_lockscreen*' } | Measure-Object | Select-Object -ExpandProperty Count"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        count = int(res.stdout.strip() or "0")
        return count > 0
    except Exception:
        return False


def launch_lockscreen_silent():
    """Launch the 4K Live Lock Screen immediately."""
    print("[SENTINEL] Laptop resumed from sleep! Launching 4K Live Lock Screen...")
    file_url = "file:///" + HTML_PATH.replace("\\", "/")
    cmd = [
        EDGE_EXE,
        f"--app={file_url}",
        f"--user-data-dir={LOCK_PROFILE}",
        "--kiosk",
        "--edge-kiosk-type=fullscreen",
        "--start-fullscreen",
        "--disable-pinch",
        "--overscroll-history-navigation=0",
        "--no-first-run"
    ]
    subprocess.Popen(cmd)


def run_sentinel(sleep_threshold_sec: float = 5.0, check_interval_sec: float = 1.5):
    """
    Continuous sleep-wake sensory loop.
    When laptop lid closes, CPU halts.
    When lid opens, time delta exceeds threshold, triggering lockscreen.
    """
    print("=" * 65)
    print("  NARUTO 4K LIVE LOCK SCREEN — AUTO-WAKE SENTINEL ACTIVE")
    print("=" * 65)
    print(f"Monitoring laptop sleep & wake events (threshold: {sleep_threshold_sec}s)...")
    print("Every time you open your laptop, the live lockscreen will appear.\n")

    while True:
        t_before = time.time()
        time.sleep(check_interval_sec)
        t_after = time.time()

        elapsed = t_after - t_before
        # If elapsed time exceeds threshold by more than double normal interval, system was asleep!
        if elapsed > sleep_threshold_sec:
            print(f"[SENTINEL] System woke after {elapsed:.1f}s sleep/lid-close.")
            launch_lockscreen_silent()


def main():
    run_sentinel()


if __name__ == "__main__":
    main()
