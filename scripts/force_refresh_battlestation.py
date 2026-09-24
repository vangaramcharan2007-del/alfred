#!/usr/bin/env python3
"""
Jarvis X - Force Refresh Battlestation & Live Desktop Sync
1. Reliably forces Windows 11 wallpaper refresh (overwriting TranscodedWallpaper cache).
2. Cleanly restarts Rainmeter so in-memory state is flushed and centered clock loads dead-center.
3. Completely kills and disables the old top-left GhostMinimal clock.
"""

import os
import sys
import shutil
import ctypes
import subprocess
import time

WALLPAPER_PATH = os.path.abspath(r"assets\wallpapers\naruto_4k_lockscreen.jpg")
TRANSCODED_WP = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Themes\TranscodedWallpaper")
RAINMETER_INI = os.path.expanduser(r"~\AppData\Roaming\Rainmeter\Rainmeter.ini")
RAINMETER_EXE = r"C:\Program Files\Rainmeter\Rainmeter.exe"


def force_set_wallpaper(img_path: str):
    print(f"[*] Applying Wallpaper: {img_path}")
    if not os.path.exists(img_path):
        print(f"[!] Wallpaper not found: {img_path}")
        return False

    # 1. Overwrite TranscodedWallpaper cache directly
    try:
        shutil.copyfile(img_path, TRANSCODED_WP)
        print("[+] Overwritten Windows Themes TranscodedWallpaper cache.")
    except Exception as e:
        print(f"[!] Warning copying TranscodedWallpaper: {e}")

    # 2. Update Registry
    try:
        cmd = f'Set-ItemProperty -Path "HKCU:\\Control Panel\\Desktop" -Name WallPaper -Value "{img_path}"'
        subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=False)
        print("[+] Registry WallPaper path updated.")
    except Exception as e:
        print(f"[!] Registry update warning: {e}")

    # 3. SystemParametersInfo Win32 Broadcast
    res = ctypes.windll.user32.SystemParametersInfoW(20, 0, img_path, 3)
    print(f"[+] Win32 SPI_SETDESKWALLPAPER broadcast: {bool(res)}")

    # 4. Trigger UpdatePerUserSystemParameters
    subprocess.run(["rundll32.exe", "user32.dll,UpdatePerUserSystemParameters", "1,", "True"], check=False)
    print("[+] User32 UpdatePerUserSystemParameters triggered.")
    return True


def ensure_rainmeter_ini():
    """Ensure Rainmeter.ini strictly has GhostMinimal disabled and JarvisAestheticClock centered."""
    if not os.path.exists(RAINMETER_INI):
        return

    with open(RAINMETER_INI, "r", encoding="utf-16", errors="ignore") as f:
        content = f.read()

    import re
    # Disable GhostMinimal
    content = re.sub(r"\[GhostMinimal\\Clock\][^\[]*", lambda m: "[GhostMinimal\\Clock]\nActive=0\n", content)

    # Disable all other stray clocks
    for c in ["DemonSlayerTanjiro\\Clock", "ArthurMorganRDR\\Clock", "BatmanGotham\\Clock", "Gear5Nika\\Clock", "Mond\\Clock"]:
        content = re.sub(rf"\[{re.escape(c)}\][^\[]*", lambda m, sc=c: f"[{sc}]\nActive=0\n", content)

    # Configure JarvisAestheticClock dead center
    clock_sec = (
        "[JarvisAestheticClock]\n"
        "Active=1\n"
        "WindowX=50%\n"
        "WindowY=25%\n"
        "AnchorX=50%\n"
        "AnchorY=50%\n"
        "ClickThrough=0\n"
        "Draggable=1\n"
        "SnapToScreen=0\n"
        "KeepOnScreen=1\n"
        "AlwaysOnTop=-2\n"
    )

    if "[JarvisAestheticClock]" in content:
        content = re.sub(r"\[JarvisAestheticClock\][^\[]*", lambda m: clock_sec, content)
    else:
        content += f"\n{clock_sec}\n"

    with open(RAINMETER_INI, "w", encoding="utf-16") as f:
        f.write(content)
    print("[+] Rainmeter.ini configured: Old clocks disabled, JarvisAestheticClock centered at (50%, 25%).")


def restart_rainmeter():
    print("[*] Killing existing Rainmeter process to clear in-memory state...")
    subprocess.run(["taskkill", "/F", "/IM", "Rainmeter.exe"], capture_output=True, check=False)
    time.sleep(1.5)

    print("[*] Launching fresh Rainmeter instance...")
    subprocess.Popen([RAINMETER_EXE], shell=False)
    time.sleep(2)
    print("[+] Fresh Rainmeter instance running with centered aesthetic clock.")


if __name__ == "__main__":
    wp = sys.argv[1] if len(sys.argv) > 1 else WALLPAPER_PATH
    force_set_wallpaper(wp)
    ensure_rainmeter_ini()
    restart_rainmeter()
