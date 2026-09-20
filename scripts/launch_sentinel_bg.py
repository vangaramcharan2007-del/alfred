"""
Direct Background Sentinel Daemon Controller (Pure Python & Win32).
===================================================================
Manages the Naruto 4K Live Lock Screen Sentinel:
- Terminates any previous pythonw instances cleanly
- Configures Windows Startup shortcut directly via COM
- Launches the detached background pythonw daemon
"""

import os
import sys
import subprocess
import time
import win32com.client

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHONW = r"C:\Users\vanga\AppData\Local\Programs\Python\Python311\pythonw.exe"
SENTINEL_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "auto_wake_sentinel.py")
STARTUP_DIR = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
LNK_PATH = os.path.join(STARTUP_DIR, "NarutoAutoWakeSentinel.lnk")


def stop_prior_sentinel():
    """Kill any prior pythonw processes cleanly."""
    try:
        subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe"], capture_output=True)
    except Exception:
        pass


def configure_startup_shortcut():
    """Create or update Windows Startup shortcut via WScript.Shell COM object."""
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(LNK_PATH)
        shortcut.TargetPath = PYTHONW
        shortcut.Arguments = f'"{SENTINEL_SCRIPT}"'
        shortcut.WorkingDirectory = PROJECT_ROOT
        shortcut.WindowStyle = 7  # Minimized / Hidden
        shortcut.Description = "Naruto 4K Live Lock Screen Auto-Wake Sentinel"
        shortcut.Save()
        print(f"[OK] Startup shortcut created: {LNK_PATH}")
        return True
    except Exception as e:
        print(f"[ERR] Failed to configure startup shortcut: {e}")
        return False


def start_sentinel_daemon() -> int:
    """Launch sentinel detached in background with zero window and closed standard streams."""
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    p = subprocess.Popen(
        [PYTHONW, SENTINEL_SCRIPT],
        cwd=PROJECT_ROOT,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True
    )
    print(f"[OK] Upgraded Auto-Wake Sentinel running in background (PID: {p.pid})")
    return p.pid


def main():
    print("=" * 65)
    print("  NARUTO LIVE LOCK SCREEN — SENTINEL SERVICE MANAGER")
    print("=" * 65)
    print("1. Stopping existing instances...")
    stop_prior_sentinel()
    time.sleep(0.5)

    print("2. Configuring Windows Startup shortcut...")
    configure_startup_shortcut()

    print("3. Starting new background daemon...")
    pid = start_sentinel_daemon()

    print("\n[ACTIVE] Naruto 4K Live Lock Screen Auto-Wake Sentinel is active.")
    print("Zero clicks needed. It will auto-activate on lid open / wake / unlock.")


if __name__ == "__main__":
    main()
