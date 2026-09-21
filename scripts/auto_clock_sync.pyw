"""
Jarvis X - Background Silent Auto Clock Sync (pyw)
Runs completely headless with zero console window.
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path

LOCAL_APPDATA = Path(os.environ.get("LOCALAPPDATA", ""))
LIVELY_PKG_DIR = LOCAL_APPDATA / "Packages" / "12030rocksdanister.LivelyWallpaper_97hta09mmv6hy" / "LocalCache" / "Local" / "Lively Wallpaper"
LAYOUT_JSON = LIVELY_PKG_DIR / "WallpaperLayout.json"
RAINMETER_EXE = Path(r"C:\Program Files\Rainmeter\Rainmeter.exe")

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
    raw = Path(raw_path_str)
    path_str = str(raw)
    if "AppData\\Local\\Lively Wallpaper" in path_str:
        rel = path_str.split("AppData\\Local\\Lively Wallpaper", 1)[1].lstrip("\\/")
        return LIVELY_PKG_DIR / rel
    return raw

def get_current_wallpaper_title() -> str:
    if not LAYOUT_JSON.exists():
        return ""
    try:
        with open(LAYOUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        for screen in data:
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
                    return str(info_dir.name)
    except Exception:
        pass
    return ""

def match_theme(title: str):
    t_lower = title.lower()
    for keywords, target in THEME_MAP:
        for kw in keywords:
            if kw in t_lower:
                return target
    return ("GhostMinimal\\Clock", "clock.ini", "Ghost Tactical Red")

def activate_theme(config_name: str, ini_file: str):
    # Hide console popup during subprocess calls
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0

    for cfg in ALL_CLOCKS:
        if cfg != config_name:
            subprocess.run([str(RAINMETER_EXE), "!DeactivateConfig", cfg], startupinfo=si, capture_output=True)
    time.sleep(0.2)
    subprocess.run([str(RAINMETER_EXE), "!ActivateConfig", config_name, ini_file], startupinfo=si, capture_output=True)
    subprocess.run([str(RAINMETER_EXE), "!Move", "50%", "110", config_name], startupinfo=si, capture_output=True)
    subprocess.run([str(RAINMETER_EXE), "!RefreshApp"], startupinfo=si, capture_output=True)

def main():
    last_title = None
    last_applied = None
    while True:
        try:
            curr_title = get_current_wallpaper_title()
            if curr_title and curr_title != last_title:
                last_title = curr_title
                config_name, ini_file, _ = match_theme(curr_title)
                if config_name != last_applied:
                    activate_theme(config_name, ini_file)
                    last_applied = config_name
        except Exception:
            pass
        time.sleep(1.0)

if __name__ == "__main__":
    main()
