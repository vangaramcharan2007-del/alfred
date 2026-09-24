#!/usr/bin/env python3
"""
Jarvis X - Wallpaper Chameleon Sentinel Daemon
Monitors Windows wallpaper changes in real-time and automatically adapts
JarvisChameleonClock's aesthetic accent colors and screen placement.
"""

import os
import sys
import time
import winreg
import subprocess

# Ensure project root is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.wallpaper_chameleon_engine import run_chameleon, get_active_wallpaper

TRANSCODED_WALLPAPER = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Themes\TranscodedWallpaper")

def get_wallpaper_mtime():
    """Returns the last modified timestamp of TranscodedWallpaper if it exists."""
    if os.path.exists(TRANSCODED_WALLPAPER):
        try:
            return os.path.getmtime(TRANSCODED_WALLPAPER)
        except OSError:
            pass
    return 0

def get_registry_wallpaper():
    """Returns current wallpaper path from HKCU registry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop")
        val, _ = winreg.QueryValueEx(key, "WallPaper")
        winreg.CloseKey(key)
        return val
    except Exception:
        return ""

def start_sentinel(poll_interval=2.0, max_iterations=None):
    """
    Continuous background loop that monitors wallpaper changes with ~0% CPU overhead.
    Seamlessly supports both Lively Wallpaper (video/animated) and Windows Desktop wallpapers.
    """
    print("[*] Starting Jarvis Wallpaper Chameleon Sentinel...")
    last_wp, _ = get_active_wallpaper()
    last_mtime = os.path.getmtime(last_wp) if (last_wp and os.path.exists(last_wp)) else 0
    
    # Run initial sync on startup
    print("[*] Performing initial sync...")
    run_chameleon()
    print("[+] Initial sync complete. Sentinel is actively watching for wallpaper changes.")

    iterations = 0
    try:
        while True:
            time.sleep(poll_interval)
            current_wp, _ = get_active_wallpaper()
            current_mtime = os.path.getmtime(current_wp) if (current_wp and os.path.exists(current_wp)) else 0

            changed = False
            if current_wp != last_wp or (current_mtime != 0 and current_mtime != last_mtime):
                print(f"\n[!] Wallpaper change detected: {current_wp} (mtime: {current_mtime})")
                changed = True
                last_wp = current_wp
                last_mtime = current_mtime

            if changed:
                time.sleep(0.5)
                print("[*] Adapting clock colors, typography & placement to new wallpaper...")
                run_chameleon(wallpaper_path=current_wp)

            iterations += 1
            if max_iterations and iterations >= max_iterations:
                break
    except KeyboardInterrupt:
        print("\n[*] Sentinel stopped by user.")

if __name__ == "__main__":
    max_iter = int(sys.argv[1]) if len(sys.argv) > 1 else None
    start_sentinel(poll_interval=2.0, max_iterations=max_iter)
