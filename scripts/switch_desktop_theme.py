"""
Jarvis X - Aesthetic Desktop Theme Switcher
Seamlessly swaps 4K Wallpaper + Matching Transparent Rainmeter Clock in 1 second.
"""
import sys
import os
import ctypes
import subprocess
import time
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
WALLPAPERS_DIR = ROOT_DIR / "assets" / "wallpapers"
RAINMETER_EXE = Path(r"C:\Program Files\Rainmeter\Rainmeter.exe")
RAINMETER_INI = Path(os.environ.get("APPDATA", "")) / "Rainmeter" / "Rainmeter.ini"

THEMES = {
    "ghost": {
        "name": "Ghost Tactical Red",
        "wallpaper": WALLPAPERS_DIR / "ghost_cod_4k.png",
        "skin_config": "GhostMinimal\\Clock",
        "skin_file": "clock.ini",
        "x": "50%",
        "y": "110",
        "anchor_x": "50%"
    },
    "naruto": {
        "name": "Naruto Sage Mode Chakra",
        "wallpaper": WALLPAPERS_DIR / "naruto_4k_lockscreen.jpg",
        "skin_config": "NarutoSage\\Clock",
        "skin_file": "clock.ini",
        "x": "50%",
        "y": "90",
        "anchor_x": "50%"
    },
    "kyoto": {
        "name": "Kyoto Pagoda Twilight",
        "wallpaper": WALLPAPERS_DIR / "kyoto_pagoda_twilight.jpg",
        "skin_config": "KyotoSunset\\Clock",
        "skin_file": "clock.ini",
        "x": "50%",
        "y": "80",
        "anchor_x": "50%"
    },
    "mond": {
        "name": "Mond Classic Aesthetic",
        "wallpaper": WALLPAPERS_DIR / "kyoto_pagoda_twilight.jpg",
        "skin_config": "Mond\\Clock",
        "skin_file": "Clock.ini",
        "x": "50%",
        "y": "80",
        "anchor_x": "50%"
    }
}

def set_wallpaper(image_path: Path):
    if not image_path.exists():
        print(f"[-] Wallpaper not found: {image_path}")
        return False
    # SPI_SETDESKWALLPAPER = 20, SPIF_UPDATEINIFILE = 1, SPIF_SENDCHANGE = 2
    res = ctypes.windll.user32.SystemParametersInfoW(20, 0, str(image_path.resolve()), 3)
    if res:
        print(f"[+] Wallpaper updated to: {image_path.name}")
        return True
    else:
        print(f"[-] Failed to update wallpaper")
        return False

def activate_rainmeter_clock(theme_key: str):
    theme = THEMES[theme_key]
    if not RAINMETER_EXE.exists():
        print("[-] Rainmeter not installed.")
        return

    # Deactivate all known clocks first
    for k, t in THEMES.items():
        subprocess.run([str(RAINMETER_EXE), "!DeactivateConfig", t["skin_config"]], capture_output=True)
    
    # Wait brief moment
    time.sleep(0.3)

    # Activate requested clock
    config_name = theme["skin_config"]
    file_name = theme["skin_file"]
    subprocess.run([str(RAINMETER_EXE), "!ActivateConfig", config_name, file_name], capture_output=True)
    time.sleep(0.3)

    # Set position
    subprocess.run([str(RAINMETER_EXE), "!Move", theme["x"], theme["y"], config_name], capture_output=True)
    subprocess.run([str(RAINMETER_EXE), "!RefreshApp"], capture_output=True)
    print(f"[+] Rainmeter clock activated: {config_name}")

def apply_theme(theme_name: str):
    key = theme_name.lower().strip()
    if key not in THEMES:
        print(f"Unknown theme '{theme_name}'. Available themes: {list(THEMES.keys())}")
        return False

    theme = THEMES[key]
    print(f"[*] Applying Theme: {theme['name']}...")
    set_wallpaper(theme["wallpaper"])
    activate_rainmeter_clock(key)
    print(f"[SUCCESS] Theme '{theme['name']}' is now LIVE on your desktop!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python switch_desktop_theme.py <ghost|naruto|kyoto|mond>")
        print(f"Available themes: {list(THEMES.keys())}")
    else:
        apply_theme(sys.argv[1])
