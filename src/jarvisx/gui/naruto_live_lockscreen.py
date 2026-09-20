"""
Naruto 4K Live Wallpaper Lock Screen Controller & Daemon.
=========================================================
Runs hardware-accelerated 4K 60FPS live video wallpaper lockscreen
with dynamic real-time digital clock, full calendar date, Shinobi HUD,
and fluid unlock mechanics.
"""

import os
import sys
import time
import subprocess
import shutil
from typing import Optional

# Paths
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(MODULE_DIR, "..", "..", ".."))
HTML_PATH = os.path.join(MODULE_DIR, "naruto_lockscreen.html")
WALLPAPER_DIR = os.path.join(PROJECT_ROOT, "assets", "wallpapers")
PRIMARY_VIDEO = r"E:\naruto-endless-sky.3840x2160.mp4"
BACKUP_VIDEO = os.path.join(WALLPAPER_DIR, "naruto_live_lockscreen.mp4")
FRAME_IMAGE = os.path.join(WALLPAPER_DIR, "naruto_4k_lockscreen.jpg")

# Known Browser Executables on Windows
BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_browser() -> Optional[str]:
    """Find available Chrome or Edge browser executable."""
    for path in BROWSER_CANDIDATES:
        if os.path.exists(path):
            return path
    which_chrome = shutil.which("chrome.exe")
    if which_chrome:
        return which_chrome
    which_edge = shutil.which("msedge.exe")
    if which_edge:
        return which_edge
    return None


def get_active_video_path() -> str:
    """Return the accessible video file path."""
    if os.path.exists(PRIMARY_VIDEO):
        return PRIMARY_VIDEO
    if os.path.exists(BACKUP_VIDEO):
        return BACKUP_VIDEO
    return PRIMARY_VIDEO


def launch_lockscreen(fullscreen: bool = True, timeout: Optional[float] = None, sync_native: bool = True) -> subprocess.Popen:
    """Launch the 4K Naruto live lock screen in dedicated app mode."""
    if sync_native:
        try:
            sync_windows_lockscreen()
        except Exception as e:
            print(f"[WARN] Native lockscreen sync warning: {e}")

    browser_exe = find_browser()
    if not browser_exe:
        raise RuntimeError("No compatible Chromium/Edge browser found to host GPU-accelerated lock screen.")

    file_url = f"file:///{os.path.abspath(HTML_PATH).replace(os.sep, '/')}"
    args = [
        browser_exe,
        f"--app={file_url}",
        "--disable-pinch",
        "--overscroll-history-navigation=0",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    if fullscreen:
        args.extend(["--start-fullscreen", "--kiosk"])
    else:
        args.append("--window-size=1280,720")

    print(f"[LOCKSCREEN] Launching Naruto 4K Live Lock Screen via: {os.path.basename(browser_exe)}")
    print(f"[LOCKSCREEN] URL: {file_url}")

    proc = subprocess.Popen(args)

    if timeout and timeout > 0:
        print(f"[LOCKSCREEN] Running for {timeout}s timeout...")
        try:
            time.sleep(timeout)
        finally:
            print("[LOCKSCREEN] Terminating lockscreen process...")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()

    return proc


def sync_windows_lockscreen() -> bool:
    """Synchronize the 4K frame to Windows native lock screen (Win + L) using official WinRT API."""
    ps_script = os.path.join(PROJECT_ROOT, "scripts", "set_user_lockscreen.ps1")
    if os.path.exists(ps_script):
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(res.stdout)
        if res.returncode == 0:
            print("[OK] Windows Native Lock Screen updated via WinRT API.")
            return True
        else:
            print(f"[WARN] WinRT LockScreen update warning: {res.stderr}")
    return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Naruto 4K Live Wallpaper Lock Screen")
    parser.add_argument("--windowed", action="store_true", help="Launch in windowed mode instead of fullscreen")
    parser.add_argument("--sync", action="store_true", help="Sync Windows native lock screen image (Win + L)")
    parser.add_argument("--timeout", type=float, default=None, help="Auto-close after N seconds (for testing)")
    args = parser.parse_args()

    if args.sync:
        sync_windows_lockscreen()

    launch_lockscreen(fullscreen=not args.windowed, timeout=args.timeout)


if __name__ == "__main__":
    main()
