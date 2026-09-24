#!/usr/bin/env python3
"""
Jarvis X - Battlestation & Theme Coordinator
Sets the desktop wallpaper, synchronizes the centered aesthetic clock palette,
and manages Rainmeter active skins for the ultimate anime/cyberpunk desktop.
"""

import os
import sys
import ctypes
import subprocess

WALLPAPER_MAP = {
    "naruto": os.path.abspath(r"assets\wallpapers\naruto_4k_lockscreen.jpg"),
    "kyoto": os.path.abspath(r"assets\wallpapers\kyoto_pagoda_twilight.jpg"),
    "ghost": os.path.abspath(r"assets\wallpapers\ghost_cod_4k.png"),
    "aesthetic": r"C:\Users\vanga\Pictures\aesthetic_wallpaper.jpg",
}

PALETTE_MAP = {
    "tokyo": 1,
    "cyberpunk": 1,
    "naruto": 2,
    "sage": 2,
    "nika": 3,
    "luffy": 3,
    "tanjiro": 4,
    "demonslayer": 4,
    "crimson": 4,
    "batman": 5,
    "gotham": 5,
}

RAINMETER_EXE = r"C:\Program Files\Rainmeter\Rainmeter.exe"
RAINMETER_INI = os.path.expanduser(r"~\AppData\Roaming\Rainmeter\Rainmeter.ini")
CLOCK_INI = r"C:\Users\vanga\OneDrive\Documents\Rainmeter\Skins\JarvisAestheticClock\Clock.ini"


def set_wallpaper(image_path: str) -> bool:
    """Set the Windows desktop wallpaper immediately via Win32 API."""
    if not os.path.exists(image_path):
        print(f"[!] Wallpaper not found at: {image_path}")
        return False
    # SPI_SETDESKWALLPAPER = 20, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE = 0x01 | 0x02 = 3
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    if result:
        print(f"[+] Desktop wallpaper applied successfully: {os.path.basename(image_path)}")
        return True
    else:
        print("[!] Failed to set desktop wallpaper.")
        return False


def set_clock_palette(mode: int):
    """Update PaletteMode in JarvisAestheticClock and refresh it."""
    if not os.path.exists(CLOCK_INI):
        print(f"[!] Clock.ini not found at {CLOCK_INI}")
        return

    try:
        with open(CLOCK_INI, "r", encoding="utf-16", errors="ignore") as f:
            content = f.read()

        import re
        content = re.sub(r"PaletteMode=\d+", f"PaletteMode={mode}", content)

        with open(CLOCK_INI, "w", encoding="utf-16") as f:
            f.write(content)

        subprocess.run([RAINMETER_EXE, "!Refresh", "JarvisAestheticClock"], check=False)
        print(f"[+] Clock palette set to mode {mode} and refreshed.")
    except Exception as e:
        print(f"[!] Error updating clock palette: {e}")


def apply_theme(theme_name: str = "naruto"):
    theme_key = theme_name.lower().strip()
    print("=" * 60)
    print(f"  ACTIVATING BATTLESTATION THEME: {theme_key.upper()}")
    print("=" * 60)

    # 1. Set Clock Palette
    palette_mode = PALETTE_MAP.get(theme_key, 1)
    set_clock_palette(palette_mode)

    # 2. Set Wallpaper
    wp_path = WALLPAPER_MAP.get(theme_key)
    if wp_path:
        set_wallpaper(wp_path)
    else:
        print(f"[i] Using current wallpaper. Available wallpaper presets: {list(WALLPAPER_MAP.keys())}")

    # 3. Ensure Rainmeter position is centered
    subprocess.run([RAINMETER_EXE, "!Move", "50%", "28%", "JarvisAestheticClock"], check=False)
    subprocess.run([RAINMETER_EXE, "!DeactivateConfig", "GhostMinimal\\Clock"], check=False)

    print("\n[+] Theme setup complete!")
    print(f"    - Clock: Jarvis Centered Aesthetic Clock (Palette: {palette_mode})")
    print(f"    - Position: WindowX=50%, WindowY=28% (Middle of Screen)")
    print(f"    - Old top-left clock: Deactivated")
    print("=" * 60)


if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "naruto"
    apply_theme(choice)
