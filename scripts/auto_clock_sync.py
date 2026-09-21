"""
Jarvis X - Automatic Lively Wallpaper Clock Sync Daemon
Monitors Lively Wallpaper's active wallpaper in real time and automatically
switches the Rainmeter clock to the matching aesthetic theme with zero user effort.
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path

# Paths
LOCAL_APPDATA = Path(os.environ.get("LOCALAPPDATA", ""))
LIVELY_PKG_DIR = LOCAL_APPDATA / "Packages" / "12030rocksdanister.LivelyWallpaper_97hta09mmv6hy" / "LocalCache" / "Local" / "Lively Wallpaper"
LAYOUT_JSON = LIVELY_PKG_DIR / "WallpaperLayout.json"
RAINMETER_EXE = Path(r"C:\Program Files\Rainmeter\Rainmeter.exe")

# Keyword to Theme mapping
THEME_MAP = [
    (["ghost"], ("GhostMinimal\\Clock", "clock.ini", "Ghost Tactical Red")),
    (["gear-5", "gear5", "nika", "luffy"], ("Gear5Nika\\Clock", "clock.ini", "Sun God Nika Gear 5")),
    (["tanjiro", "akaza", "demon"], ("DemonSlayerTanjiro\\Clock", "clock.ini", "Tanjiro Hinokami Kagura")),
    (["spider", "spiderman", "crimson-sky"], ("SpiderManCrimson\\Clock", "clock.ini", "Spider-Man Crimson Sky")),
    (["batman", "gotham"], ("BatmanGotham\\Clock", "clock.ini", "Batman Gotham Rain")),
    (["naruto", "sage"], ("NarutoSage\\Clock", "clock.ini", "Naruto Sage Mode")),
    (["arthur", "rdr", "sunset", "minecraft"], ("ArthurMorganRDR\\Clock", "clock.ini", "Outlaw Sunset")),
    (["matrix"], ("MatrixRain\\Clock", "clock.ini", "Matrix Cyberpunk Green"))
]

ALL_CLOCKS = [
    "GhostMinimal\\Clock",
    "Gear5Nika\\Clock",
    "DemonSlayerTanjiro\\Clock",
    "SpiderManCrimson\\Clock",
    "BatmanGotham\\Clock",
    "NarutoSage\\Clock",
    "ArthurMorganRDR\\Clock",
    "MatrixRain\\Clock",
    "Mond\\Clock"
]

def resolve_lively_info_path(raw_path_str: str) -> Path:
    """Resolve redirected UWP Lively path to real LocalCache path."""
    raw = Path(raw_path_str)
    # If path starts with C:\Users\<user>\AppData\Local\Lively Wallpaper
    # Redirect to Packages\...
    path_str = str(raw)
    if "AppData\\Local\\Lively Wallpaper" in path_str:
        rel = path_str.split("AppData\\Local\\Lively Wallpaper", 1)[1].lstrip("\\/")
        real_path = LIVELY_PKG_DIR / rel
        return real_path
    return raw

def get_current_wallpaper_title() -> str:
    """Extract current wallpaper title from WallpaperLayout.json"""
    if not LAYOUT_JSON.exists():
        return ""

    try:
        with open(LAYOUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for screen in data:
            if screen.get("LivelyScreen", {}).get("IsPrimary", False) or True:
                info_path_raw = screen.get("LivelyInfoPath")
                if info_path_raw:
                    info_dir = resolve_lively_info_path(info_path_raw)
                    info_json = info_dir / "LivelyInfo.json"
                    if info_json.exists():
                        with open(info_json, "r", encoding="utf-8") as inf:
                            meta = json.load(inf)
                            title = meta.get("Title", "") or meta.get("FileName", "")
                            return str(title)
                    else:
                        # Use folder or path name as fallback
                        return str(info_dir.name)
    except Exception as e:
        pass
    return ""

def match_theme(title: str):
    t_lower = title.lower()
    for keywords, target in THEME_MAP:
        for kw in keywords:
            if kw in t_lower:
                return target
    # Default fallback
    return ("GhostMinimal\\Clock", "clock.ini", "Ghost Tactical Red")

def activate_theme(config_name: str, ini_file: str, desc: str):
    print(f"[*] AUTO-SWITCH: Active wallpaper matches '{desc}' -> Activating {config_name}")
    # Deactivate others
    for cfg in ALL_CLOCKS:
        if cfg != config_name:
            subprocess.run([str(RAINMETER_EXE), "!DeactivateConfig", cfg], capture_output=True)
    time.sleep(0.2)
    # Activate target
    subprocess.run([str(RAINMETER_EXE), "!ActivateConfig", config_name, ini_file], capture_output=True)
    subprocess.run([str(RAINMETER_EXE), "!Move", "50%", "110", config_name], capture_output=True)
    subprocess.run([str(RAINMETER_EXE), "!RefreshApp"], capture_output=True)
    print(f"[SUCCESS] {desc} is now active!")

def run_daemon():
    print("=== Jarvis X Auto Clock Sync Daemon Started ===")
    print("Listening to Lively Wallpaper changes in real time...")
    
    last_title = None
    last_applied_theme = None
    
    while True:
        try:
            curr_title = get_current_wallpaper_title()
            if curr_title and curr_title != last_title:
                print(f"[DETECTED] Lively Wallpaper changed to: '{curr_title}'")
                last_title = curr_title
                
                config_name, ini_file, desc = match_theme(curr_title)
                if config_name != last_applied_theme:
                    activate_theme(config_name, ini_file, desc)
                    last_applied_theme = config_name
        except Exception as e:
            pass
        time.sleep(1.0)  # Ultra-lightweight 1-second check, zero CPU impact

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        title = get_current_wallpaper_title()
        print(f"Current detected wallpaper: '{title}'")
        cfg, ini, desc = match_theme(title)
        activate_theme(cfg, ini, desc)
    else:
        run_daemon()
