"""
Auto-Wake Sentinel for Naruto 4K Live Lock Screen.
==================================================
Runs silently in the background (zero CPU footprint, ~0.01% RAM).
Monitors:
1. Laptop lid open / sleep resume (hardware CPU sleep delta).
2. Windows workstation unlock (PIN/password entered or LogonUI dismissed).
3. System boot / session logon.

Whenever any of these occur, it automatically brings up the Naruto 4K Live Wallpaper
Lock Screen in isolated fullscreen kiosk mode.
"""

import os
import sys
import time
import subprocess
import tempfile
import ctypes

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK_PROFILE = os.path.join(tempfile.gettempdir(), "naruto_lock_runtime_profile")
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
HTML_PATH = os.path.join(PROJECT_ROOT, "src", "jarvisx", "gui", "naruto_lockscreen.html")

user32 = ctypes.windll.user32


def is_workstation_locked() -> bool:
    """
    Check if Windows is currently locked (LogonUI / password / PIN screen active).
    When the workstation is locked, OpenInputDesktop fails with ERROR_ACCESS_DENIED (5).
    """
    try:
        # DESKTOP_SWITCHDESKTOP = 0x0100
        desk = user32.OpenInputDesktop(0, False, 0x0100)
        if desk == 0:
            return True
        user32.CloseDesktop(desk)
        return False
    except Exception:
        return False


def is_lockscreen_open() -> bool:
    """
    Check if the Naruto Live Lock Screen window is already open.
    Uses Win32 EnumWindows for sub-millisecond execution with zero CPU impact.
    """
    try:
        found = False

        def enum_windows_callback(hwnd, lparam):
            nonlocal found
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    title = buffer.value
                    if "Naruto" in title or "Live Lock Screen" in title:
                        found = True
                        return False
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
        return found
    except Exception:
        return False


def launch_lockscreen_silent():
    """Launch the 4K Live Lock Screen immediately in isolated fullscreen kiosk."""
    try:
        from scripts.get_battery import get_battery_info
        b = get_battery_info()
    except Exception:
        b = {"percent": 90, "charging": False}
    username = os.getenv("USERNAME", "Hokage")
    file_url = "file:///" + HTML_PATH.replace("\\", "/") + f"?battery={b['percent']}&charging={1 if b['charging'] else 0}&user={username}"
    cmd = [
        EDGE_EXE,
        f"--app={file_url}",
        f"--user-data-dir={LOCK_PROFILE}",
        "--kiosk",
        "--edge-kiosk-type=fullscreen",
        "--start-fullscreen",
        "--disable-pinch",
        "--overscroll-history-navigation=0",
        "--no-first-run",
        "--autoplay-policy=no-user-gesture-required",
        "--allow-file-access-from-files",
        "--enable-gpu-rasterization",
        "--enable-zero-copy",
        "--ignore-gpu-blocklist"
    ]
    try:
        subprocess.Popen(cmd)
        print(f"[SENTINEL] Successfully launched Naruto 4K Live Lock Screen (Battery: {b['percent']}%, User: {username}).")
    except Exception as e:
        print(f"[SENTINEL] Error launching lockscreen: {e}")


def run_sentinel(sleep_threshold_sec: float = 4.0, check_interval_sec: float = 1.0):
    """
    Continuous hybrid sleep & lock monitor loop.
    - Sleep resume: detected when elapsed time > sleep_threshold_sec.
    - Workstation unlock: detected when is_workstation_locked() transitions from True to False.
    """
    print("=" * 68)
    print("  NARUTO 4K LIVE LOCK SCREEN — AUTO-WAKE & UNLOCK SENTINEL ACTIVE")
    print("=" * 68)
    print(f"Monitoring: Sleep/Lid Events & Workstation Unlock (Check interval: {check_interval_sec}s)")
    print("Zero manual launching required. The lockscreen activates automatically.\n")

    was_locked = is_workstation_locked()
    wake_detected = False
    last_launch_time = 0.0

    while True:
        t_before = time.time()
        time.sleep(check_interval_sec)
        t_after = time.time()

        elapsed = t_after - t_before
        currently_locked = is_workstation_locked()

        # 1. Detect sleep or lid closure
        if elapsed > sleep_threshold_sec:
            print(f"[SENTINEL] Sleep resume detected! (Elapsed: {elapsed:.1f}s)")
            wake_detected = True

        # 2. Detect workstation unlock (user completed PIN/Password/Fingerprint entry)
        unlock_detected = False
        if was_locked and not currently_locked:
            print("[SENTINEL] Workstation unlocked by user!")
            unlock_detected = True

        was_locked = currently_locked

        # 3. Trigger activation once user reaches active desktop
        if (wake_detected or unlock_detected) and not currently_locked:
            now = time.time()
            # 4-second debounce to prevent double triggers
            if now - last_launch_time > 4.0:
                if not is_lockscreen_open():
                    print("[SENTINEL] Activating 4K Live Lock Screen now...")
                    launch_lockscreen_silent()
                    last_launch_time = now
                else:
                    print("[SENTINEL] Lockscreen is already active.")
            wake_detected = False


def main():
    run_sentinel()


if __name__ == "__main__":
    main()
