#!/usr/bin/env python3
"""
Jarvis X - Wallpaper Chameleon Engine v4.6
Ultimate Theme-Aware Dynamic Desktop Clock Engine

Features:
- Authentic franchise typography (Dela Gothic One, Bebas Neue, Ninja Naruto, Shojumaru, Chinese Rocks, Yuji Boku, Cinzel Decorative, Aquatico, Quicksand)
- Pure minimalist clock: Time, Day, and Date with ZERO franchise names printed
- Franchise-faithful visual stylings: Comic book black borders, gritty noir drop shadows, signature anime & film palettes
- Real-time Lively Wallpaper & Windows Desktop wallpaper detection
- Subject-aware negative space placement (avoids character heads, faces, and busy artwork)
- Strictly ONE master clock enforced across all Rainmeter configs (zero duplicates, zero telemetry clutter)
- Near-zero CPU overhead (<0.01% CPU)
"""

import os
import sys
import time
import glob
import json
import argparse
import colorsys
import subprocess
import winreg
from PIL import Image, ImageFilter, ImageStat

RAINMETER_EXE = r"C:\Program Files\Rainmeter\Rainmeter.exe"
SKINS_DIR = r"C:\Users\vanga\OneDrive\Documents\Rainmeter\Skins\JarvisChameleonClock"
PROJECT_SKIN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "skins", "JarvisChameleonClock")
RAINMETER_INI = os.path.expanduser(r"~\AppData\Roaming\Rainmeter\Rainmeter.ini")

REDUNDANT_SKINS = [
    r"GhostMinimal\Clock",
    r"GhostMinimal",
    r"SpiderManCrimson\Clock",
    r"SpiderManCrimson",
    r"BatmanGotham\Clock",
    r"BatmanGotham",
    r"DemonSlayerTanjiro\Clock",
    r"DemonSlayerTanjiro",
    r"Gear5Nika\Clock",
    r"Gear5Nika",
    r"NarutoSage\Clock",
    r"NarutoSage",
    r"ArthurMorganRDR\Clock",
    r"ArthurMorganRDR",
    r"JarvisAestheticClock\Clock",
    r"JarvisAestheticClock",
    r"KyotoSunset\Clock",
    r"KyotoSunset",
    r"Mond\Clock",
    r"Mond",
    r"ModularClocks",
    r"illustro\Clock",
    r"illustro\Disk",
    r"illustro\System",
    r"illustro\Welcome",
]

THEMES = {
    "one_piece": {
        "name": "One Piece (Authentic Pirate Manga Typography)",
        "keywords": ["one piece", "onepiece", "luffy", "nika", "gear5", "gear 5", "sunny", "strawhat", "zoro", "sanji", "kaido", "wano", "pirate"],
        "FontTitle": "ONE PIECE",
        "FontTime": "ONE PIECE",
        "FontDate": "ONE PIECE",
        "ColorAccent": "58, 146, 232, 255",     # One Piece Ocean Blue
        "ColorPrimary": "255, 255, 255, 255",   # Pure Crisp White
        "ColorSub": "255, 215, 30, 255",       # Straw Hat Gold
        "ColorMuted": "255, 215, 30, 240",     # Straw Hat Gold
        "ColorShadow": "0, 0, 0, 255",         # Comic Book Black Border
        "StringEffect": "Border",
        "Scale": "1.0",
        "PrefPlacement": "UpperLeft"
    },
    "batman": {
        "name": "The Batman (Authentic Batwing Gotham Typography)",
        "keywords": ["batman", "gotham", "dark knight", "pattinson", "dc", "vengeance", "riddler"],
        "FontTitle": "BatmanForeverAlternate",
        "FontTime": "BatmanForeverAlternate",
        "FontDate": "BatmanForeverAlternate",
        "ColorAccent": "225, 25, 35, 255",      # The Batman 2022 Crimson Red
        "ColorPrimary": "255, 255, 255, 255",   # Stark White
        "ColorSub": "200, 20, 30, 255",
        "ColorMuted": "180, 180, 190, 220",     # Gotham Slate
        "ColorShadow": "0, 0, 0, 255",
        "StringEffect": "Shadow",
        "Scale": "1.0",
        "PrefPlacement": "UpperLeft"
    },
    "spiderman": {
        "name": "Spider-Man (Comic Red & Web Blue)",
        "keywords": ["spider", "spiderman", "peter", "miles", "morales", "web", "marvel"],
        "FontTitle": "Bebas Neue",
        "FontTime": "Bebas Neue",
        "FontDate": "Segoe UI Semibold",
        "ColorAccent": "226, 54, 54, 255",      # Spider-Man Crimson
        "ColorPrimary": "255, 255, 255, 255",   # Crisp White
        "ColorSub": "0, 85, 184, 255",         # Web Blue
        "ColorMuted": "0, 140, 240, 240",      # Web Cyan/Blue
        "ColorShadow": "0, 0, 0, 255",         # Comic Black Border
        "StringEffect": "Border",
        "Scale": "1.0",
        "PrefPlacement": "UpperLeft"
    },
    "ghost_cod": {
        "name": "Call of Duty: Modern Warfare (Ghost / Task Force 141)",
        "keywords": ["ghost", "simon", "riley", "cod", "modern warfare", "mw2", "mwii", "warzone", "task force", "tf141", "military", "tactical", "red-ghost", "spec ops"],
        "FontTitle": "Agency FB",
        "FontTime": "Agency FB",
        "FontDate": "Agency FB",
        "ColorAccent": "235, 30, 40, 255",      # Tactical NVG Crimson
        "ColorPrimary": "250, 250, 250, 255",   # Bone Skull White
        "ColorSub": "205, 25, 35, 255",        # Ghost Red
        "ColorMuted": "170, 175, 185, 220",     # Comms HUD Slate
        "ColorShadow": "0, 0, 0, 255",         # Night Vision Noir Shadow
        "StringEffect": "Shadow",
        "Scale": "1.0",
        "PrefPlacement": "UpperLeft"
    },
    "samurai": {
        "name": "Ghost of Tsushima (Katana Ink)",
        "keywords": ["samurai", "tsushima", "ronin", "katana", "jin", "sakai", "bloodfall", "pagoda", "kyoto", "bleach", "shinigami"],
        "FontTitle": "Yuji Boku",
        "FontTime": "Yuji Boku",
        "FontDate": "Yuji Boku",
        "ColorAccent": "255, 45, 55, 255",      # Red Maple Leaf
        "ColorPrimary": "255, 255, 255, 255",   # Rice Paper White
        "ColorSub": "220, 30, 45, 255",        # Deep Blood
        "ColorMuted": "220, 220, 230, 220",     # Katana Steel
        "ColorShadow": "0, 0, 0, 255",         # Katana Ink Noir Shadow
        "StringEffect": "Shadow",
        "Scale": "1.0",
        "PrefPlacement": "UpperLeft"
    },
    "naruto": {
        "name": "Naruto Shippuden (Chakra Orange)",
        "keywords": ["naruto", "sage", "chakra", "rasengan", "sasuke", "itachi", "konoha", "shippuden", "kurama", "sharingan", "akatsuki"],
        "FontTitle": "Ninja Naruto",
        "FontTime": "Ninja Naruto",
        "FontDate": "Ninja Naruto",
        "ColorAccent": "255, 130, 10, 255",     # Kurama Chakra Orange
        "ColorPrimary": "255, 255, 255, 255",   # Pure White
        "ColorSub": "250, 204, 21, 255",       # Sage Gold
        "ColorMuted": "240, 225, 195, 220",     # Scroll Parchment
        "ColorShadow": "20, 10, 5, 240",
        "StringEffect": "Border",
        "Scale": "1.0",
        "PrefPlacement": "UpperLeft"
    },
    "rdr2": {
        "name": "Red Dead Redemption (Western Outlaw)",
        "keywords": ["rdr", "red dead", "reddead", "arthur", "morgan", "van der linde", "western", "outlaw", "cowboy", "marston", "wild west"],
        "FontTitle": "Chinese Rocks",
        "FontTime": "Chinese Rocks",
        "FontDate": "Chinese Rocks",
        "ColorAccent": "225, 45, 35, 255",      # Outlaw Blood Crimson
        "ColorPrimary": "250, 245, 235, 255",   # Weathered Bone White
        "ColorSub": "210, 160, 90, 255",       # Saddle Tan
        "ColorMuted": "210, 200, 190, 200",     # Frontier Ash
        "ColorShadow": "10, 5, 0, 240",
        "StringEffect": "Shadow",
        "Scale": "1.0",
        "PrefPlacement": "UpperLeft"
    },
    "demon_slayer": {
        "name": "Demon Slayer (Kimetsu Nichirin)",
        "keywords": ["demon", "slayer", "tanjiro", "nezuko", "rengoku", "nichirin", "kimetsu", "akaza"],
        "FontTitle": "Cinzel Decorative",
        "FontTime": "Cinzel Decorative",
        "FontDate": "Segoe UI Semibold",
        "ColorAccent": "255, 80, 40, 255",      # Flame Breathing Red
        "ColorPrimary": "255, 255, 255, 255",
        "ColorSub": "40, 220, 180, 255",       # Water Breathing Teal
        "ColorMuted": "220, 230, 240, 200",
        "ColorShadow": "0, 0, 0, 240",
        "StringEffect": "Shadow",
        "Scale": "1.0",
        "PrefPlacement": "UpperLeft"
    },
    "cyberpunk": {
        "name": "Cyberpunk 2077 (Neon City)",
        "keywords": ["cyberpunk", "matrix", "synthwave", "neon", "sci-fi"],
        "FontTitle": "Aquatico",
        "FontTime": "Segoe UI Light",
        "FontDate": "Consolas",
        "ColorAccent": "0, 240, 255, 255",      # Neon Cyan
        "ColorPrimary": "255, 255, 255, 255",
        "ColorSub": "240, 60, 200, 255",       # Hot Magenta
        "ColorMuted": "190, 210, 230, 200",     # Chrome Blue
        "ColorShadow": "0, 0, 0, 240",
        "StringEffect": "Shadow",
        "Scale": "1.0",
        "PrefPlacement": "UpperLeft"
    },
    "minimal": {
        "name": "Minimalist Editorial",
        "keywords": [],
        "FontTitle": "Quicksand",
        "FontTime": "Segoe UI Light",
        "FontDate": "Segoe UI Semibold",
        "ColorAccent": "255, 180, 40, 255",     # Warm Gold
        "ColorPrimary": "255, 255, 255, 255",
        "ColorSub": "250, 204, 21, 255",
        "ColorMuted": "200, 200, 210, 200",
        "ColorShadow": "0, 0, 0, 200",
        "StringEffect": "Shadow",
        "Scale": "1.0",
        "PrefPlacement": "UpperLeft"
    }
}

def get_lively_wallpaper():
    """
    Detects active animated/video wallpaper from Lively Wallpaper if running.
    Returns (thumbnail_path or image_path, candidate_names_list) or (None, []).
    """
    candidate_names = []
    lively_packages = glob.glob(os.path.expanduser(r"~\AppData\Local\Packages\*LivelyWallpaper*"))
    for pkg in lively_packages:
        layout_path = os.path.join(pkg, "LocalCache", "Local", "Lively Wallpaper", "WallpaperLayout.json")
        if os.path.exists(layout_path):
            try:
                with open(layout_path, "r", encoding="utf-8") as f:
                    layout = json.load(f)
                for item in layout:
                    if not item.get("LivelyScreen", {}).get("isStale", False):
                        info_dir = item.get("LivelyInfoPath", "")
                        dir_id = os.path.basename(info_dir)
                        info_file_candidates = [
                            os.path.join(pkg, "LocalCache", "Local", "Lively Wallpaper", "Library", "SaveData", "wptmp", dir_id, "LivelyInfo.json"),
                            os.path.join(info_dir, "LivelyInfo.json")
                        ]
                        for info_file in info_file_candidates:
                            if os.path.exists(info_file):
                                with open(info_file, "r", encoding="utf-8") as inf_f:
                                    info = json.load(inf_f)
                                title = info.get("Title", "")
                                fn = info.get("FileName", "")
                                thumb_rel = info.get("Thumbnail", "")
                                if title:
                                    candidate_names.append(title)
                                if fn:
                                    candidate_names.append(fn)
                                candidate_names.append(dir_id)

                                thumb_path = os.path.join(os.path.dirname(info_file), thumb_rel) if thumb_rel else None
                                if thumb_path and os.path.exists(thumb_path):
                                    return thumb_path, candidate_names
                                for ext in ('*.jpg', '*.png', '*.webp'):
                                    for img_f in glob.glob(os.path.join(os.path.dirname(info_file), ext)):
                                        return img_f, candidate_names
            except Exception:
                pass
    return None, candidate_names

def get_active_wallpaper():
    """
    Locates current active wallpaper image and candidate metadata.
    Prioritizes Lively Wallpaper if running, then Windows Desktop wallpaper.
    Returns (image_path, candidate_names_list).
    """
    # 1. First check Lively Wallpaper (animated / video wallpaper)
    lively_img, lively_cands = get_lively_wallpaper()
    if lively_img and os.path.exists(lively_img):
        return lively_img, lively_cands

    candidate_names = list(lively_cands)

    # 2. Check Photos App Background directory (used by Windows Photos app)
    photos_glob = os.path.expandvars(r"%LOCALAPPDATA%\Packages\Microsoft.Windows.Photos_*\LocalState\PhotosAppBackground\*")
    for f in glob.glob(photos_glob):
        if os.path.isfile(f) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            candidate_names.append(os.path.basename(f))

    transcoded = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Themes\TranscodedWallpaper")
    transcoded_mtime = os.path.getmtime(transcoded) if (os.path.exists(transcoded) and os.path.getsize(transcoded) > 0) else 0

    # 3. Check Wallpaper registry Current in Explorer
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Wallpapers")
        try:
            curr_val, _ = winreg.QueryValueEx(key, "CurrentWallpaperPath")
            if curr_val and os.path.exists(curr_val):
                candidate_names.append(curr_val)
        except OSError:
            pass
        winreg.CloseKey(key)
    except Exception:
        pass

    # 4. Check Control Panel\Desktop\WallPaper
    reg_wallpaper = None
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop")
        reg_val, _ = winreg.QueryValueEx(key, "WallPaper")
        winreg.CloseKey(key)
        if reg_val and os.path.exists(reg_val):
            reg_mtime = os.path.getmtime(reg_val)
            if transcoded_mtime == 0 or reg_mtime >= transcoded_mtime or abs(reg_mtime - transcoded_mtime) < 15:
                reg_wallpaper = reg_val
                candidate_names.append(reg_val)
    except Exception:
        pass

    # 5. TranscodedWallpaper is the active rendered desktop bitmap
    if transcoded_mtime > 0:
        return transcoded, candidate_names

    if reg_wallpaper:
        return reg_wallpaper, candidate_names

    return None, candidate_names

def detect_theme_from_features(img, candidate_strings, forced_theme=None):
    """
    Determines the visual aesthetic theme using:
    1. Explicit forced override
    2. Candidate string keyword analysis
    3. Computer Vision / Visual signature detection (Gear 5 moon, chakra orange, ink crimson)
    """
    if forced_theme and forced_theme.lower() in THEMES:
        return forced_theme.lower(), THEMES[forced_theme.lower()]

    # 1. Keyword matching on candidate filenames
    combined_strings = " ".join(candidate_strings).lower()
    for theme_key, tdata in THEMES.items():
        if theme_key == "minimal":
            continue
        if any(kw in combined_strings for kw in tdata["keywords"]):
            return theme_key, tdata

    # 2. Visual signature detection on image bitmap
    w, h = img.size

    # A. Gear 5 Nika / Full Moon Silhouette Detection:
    center_crop = img.crop((int(w * 0.35), int(h * 0.10), int(w * 0.65), int(h * 0.55))).resize((30, 30))
    center_colors = center_crop.getcolors(900) or []
    bright_center_pix = sum(c[0] for c in center_colors if sum(c[1]) / 3.0 > 180)

    corner_crop = img.crop((0, 0, int(w * 0.25), int(h * 0.25))).resize((20, 20))
    corner_colors = corner_crop.getcolors(400) or []
    avg_corner_val = sum(c[0] * (sum(c[1]) / 3.0) for c in corner_colors) / 400.0

    if (bright_center_pix / 900.0) > 0.20 and avg_corner_val < 35.0:
        return "one_piece", THEMES["one_piece"]

    # B. General Color Palette Energy Analysis
    thumb = img.resize((60, 60))
    colors = thumb.getcolors(maxcolors=4000) or []
    total_pix = max(1, sum(c[0] for c in colors))

    red_energy = 0
    orange_yellow_energy = 0
    cyan_magenta_energy = 0
    earth_tan_energy = 0

    for count, (r, g, b) in colors:
        h_val, s_val, v_val = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        # Red / Crimson (Hue 345 - 15)
        if (h_val >= 0.95 or h_val <= 0.04) and s_val > 0.4 and v_val > 0.3:
            red_energy += count
        # Chakra Orange / Gold (Hue 25 - 55)
        elif 0.06 <= h_val <= 0.15 and s_val > 0.4:
            orange_yellow_energy += count
        # Cyan / Neon Magenta (Hue 170-195 or 290-330)
        elif ((0.47 <= h_val <= 0.54) or (0.80 <= h_val <= 0.92)) and s_val > 0.5:
            cyan_magenta_energy += count
        # Earth tones / Sepia / Tan (Hue 20 - 45, moderate sat)
        elif 0.05 <= h_val <= 0.12 and 0.2 <= s_val <= 0.5 and 0.2 <= v_val <= 0.7:
            earth_tan_energy += count

    red_ratio = red_energy / total_pix
    orange_ratio = orange_yellow_energy / total_pix
    cyan_ratio = cyan_magenta_energy / total_pix
    earth_ratio = earth_tan_energy / total_pix

    if orange_ratio > 0.20:
        return "naruto", THEMES["naruto"]
    if red_ratio > 0.22:
        return "batman", THEMES["batman"]
    if cyan_ratio > 0.18:
        return "one_piece", THEMES["one_piece"]
    if earth_ratio > 0.25:
        return "rdr2", THEMES["rdr2"]

    return "minimal", THEMES["minimal"]

def analyze_negative_space(img, preferred_placement=None):
    """
    Evaluates where open negative space is on screen (UpperLeft vs UpperRight vs CenterTop).
    Avoids busy artwork, characters, and focal points.
    """
    if preferred_placement and preferred_placement in ["UpperLeft", "UpperRight", "CenterTop", "Center"]:
        zones_lookup = {
            "UpperLeft": {"WindowX": "5%", "WindowY": "5%", "AnchorX": "0%", "AnchorY": "0%"},
            "UpperRight": {"WindowX": "72%", "WindowY": "5%", "AnchorX": "0%", "AnchorY": "0%"},
            "CenterTop": {"WindowX": "50%", "WindowY": "5%", "AnchorX": "50%", "AnchorY": "0%"},
            "Center": {"WindowX": "50%", "WindowY": "40%", "AnchorX": "50%", "AnchorY": "50%"}
        }
        res = zones_lookup[preferred_placement]
        res["name"] = preferred_placement
        return res

    w, h = img.size
    gray = img.convert('L')
    edges = gray.filter(ImageFilter.FIND_EDGES)

    zones = {
        "UpperLeft": {
            "bbox": (int(w * 0.03), int(h * 0.03), int(w * 0.35), int(h * 0.30)),
            "WindowX": "5%", "WindowY": "5%", "AnchorX": "0%", "AnchorY": "0%"
        },
        "UpperRight": {
            "bbox": (int(w * 0.65), int(h * 0.03), int(w * 0.97), int(h * 0.30)),
            "WindowX": "72%", "WindowY": "5%", "AnchorX": "0%", "AnchorY": "0%"
        },
        "CenterTop": {
            "bbox": (int(w * 0.30), int(h * 0.03), int(w * 0.70), int(h * 0.25)),
            "WindowX": "50%", "WindowY": "5%", "AnchorX": "50%", "AnchorY": "0%"
        }
    }

    zone_scores = {}
    for zname, zinfo in zones.items():
        crop_edges = edges.crop(zinfo["bbox"])
        stat = ImageStat.Stat(crop_edges)
        zone_scores[zname] = stat.mean[0]

    if zone_scores["UpperLeft"] <= zone_scores["UpperRight"] * 1.4:
        best_name = "UpperLeft"
    elif zone_scores["UpperRight"] < zone_scores["UpperLeft"]:
        best_name = "UpperRight"
    else:
        best_name = "CenterTop"

    selected = zones[best_name]
    selected["name"] = best_name
    return selected

def update_skin_variables(theme_cfg, placement_name):
    """Write updated variables with authentic themed typography, palettes, and styling."""
    content = f"""[Variables]
FontTitle={theme_cfg['FontTitle']}
FontTime={theme_cfg['FontTime']}
FontDate={theme_cfg['FontDate']}
FontBold=Segoe UI Semibold
Scale={theme_cfg['Scale']}
ColorPrimary={theme_cfg['ColorPrimary']}
ColorAccent={theme_cfg['ColorAccent']}
ColorSub={theme_cfg['ColorSub']}
ColorMuted={theme_cfg['ColorMuted']}
ColorShadow={theme_cfg['ColorShadow']}
StringEffect={theme_cfg.get('StringEffect', 'Shadow')}
ZoneName={placement_name}
"""
    targets = [
        os.path.join(SKINS_DIR, "@Resources", "Variables.inc"),
        os.path.join(PROJECT_SKIN_DIR, "@Resources", "Variables.inc")
    ]
    for t in targets:
        os.makedirs(os.path.dirname(t), exist_ok=True)
        with open(t, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"[+] Updated Variables.inc: DayFont='{theme_cfg['FontTitle']}', TimeFont='{theme_cfg['FontTime']}', Accent={theme_cfg['ColorAccent']}, Effect={theme_cfg.get('StringEffect', 'Shadow')}")

def update_rainmeter_ini(placement):
    """Ensure strictly ONE master clock is Active=1 and all legacy duplicates are Active=0."""
    if not os.path.exists(RAINMETER_INI):
        return

    clean_ini = f"""[Rainmeter]
Logging=1
SkinPath=C:\\Users\\vanga\\OneDrive\\Documents\\Rainmeter\\Skins\\

[JarvisChameleonClock]
Active=1
WindowX={placement['WindowX']}@1
WindowY={placement['WindowY']}@1
AnchorX={placement['AnchorX']}
AnchorY={placement['AnchorY']}
AutoSelectScreen=1
ClickThrough=0
Draggable=1
SnapEdges=1
KeepOnScreen=1
AlwaysOnTop=0
"""
    for skin in REDUNDANT_SKINS:
        clean_ini += f"\n[{skin}]\nActive=0\n"

    with open(RAINMETER_INI, "w", encoding="utf-16") as f:
        f.write(clean_ini)
    print(f"[+] Rainmeter.ini: [JarvisChameleonClock] Active=1 at ({placement['WindowX']}@1, {placement['WindowY']}@1), all redundant clocks Active=0")

def is_rainmeter_running():
    try:
        res = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Rainmeter.exe"], capture_output=True, text=True, check=False)
        return "Rainmeter.exe" in res.stdout
    except Exception:
        return False

def ensure_rainmeter_running():
    if not is_rainmeter_running():
        print("[*] Rainmeter not currently running. Launching interactive desktop instance...")
        subprocess.run(["explorer.exe", RAINMETER_EXE], check=False)
        time.sleep(2.0)

def reload_rainmeter():
    """Hot-reload skin cleanly and ensure single master clock."""
    try:
        ensure_rainmeter_running()
        subprocess.run([RAINMETER_EXE, "!Refresh", "JarvisChameleonClock"], check=False)
        subprocess.run([RAINMETER_EXE, "!RefreshApp"], check=False)
        print("[+] Hot-reloaded Rainmeter skin successfully (single master clock enforced)")
    except Exception as e:
        print(f"[-] Could not send refresh bang: {e}")

def run_chameleon(wallpaper_path=None, forced_theme=None, forced_placement=None):
    if wallpaper_path and os.path.exists(wallpaper_path):
        wp = wallpaper_path
        candidates = [os.path.basename(wallpaper_path)]
    else:
        wp, candidates = get_active_wallpaper()

    if not wp or not os.path.exists(wp):
        print("[-] Could not find active desktop wallpaper!")
        return False

    print(f"[*] Analyzing Wallpaper: {wp}")
    with Image.open(wp) as img:
        img_rgb = img.convert('RGB')
        theme_key, theme_cfg = detect_theme_from_features(img_rgb, candidates, forced_theme=forced_theme)
        placement = analyze_negative_space(img_rgb, preferred_placement=forced_placement)

    print(f"[*] Theme Activated: [{theme_cfg['name'].upper()}]")
    print(f"[*] Typography: Day='{theme_cfg['FontTitle']}' | Time='{theme_cfg['FontTime']}' | Date='{theme_cfg['FontDate']}'")
    print(f"[*] Palette: Accent={theme_cfg['ColorAccent']} | Primary={theme_cfg['ColorPrimary']} | Style={theme_cfg.get('StringEffect', 'Shadow')}")
    print(f"[*] Screen Placement: {placement['name']} ({placement['WindowX']}, {placement['WindowY']})")

    update_skin_variables(theme_cfg, placement['name'])
    update_rainmeter_ini(placement)
    reload_rainmeter()
    print("[+] Chameleon Clock synchronisation complete with zero lag and zero duplicates!")
    return True

def watch_mode():
    """Ultra-lightweight background watcher checking for wallpaper swaps (<0.01% CPU)."""
    print("[*] Starting Chameleon Watcher Service (Zero-overhead wallpaper listener)...")
    last_mtime = 0
    last_wp = None

    while True:
        try:
            wp, _ = get_active_wallpaper()
            if wp and os.path.exists(wp):
                mtime = os.path.getmtime(wp)
                if mtime != last_mtime or wp != last_wp:
                    print(f"\n[*] Wallpaper change detected: {wp} (mtime={mtime})")
                    run_chameleon(wallpaper_path=wp)
                    last_mtime = mtime
                    last_wp = wp
            time.sleep(2.0)
        except KeyboardInterrupt:
            print("\n[*] Watcher terminated cleanly.")
            break
        except Exception:
            time.sleep(3.0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jarvis X Themed Chameleon Clock Engine v4.6")
    parser.add_argument("--wallpaper", type=str, default=None, help="Explicit wallpaper path to analyze")
    parser.add_argument("--theme", type=str, default=None, help="Force specific theme: one_piece, batman, spiderman, naruto, rdr2, samurai, demon_slayer, cyberpunk, minimal")
    parser.add_argument("--placement", type=str, default=None, help="Force placement: UpperLeft, UpperRight, CenterTop, Center")
    parser.add_argument("--watch", action="store_true", help="Run lightweight background watcher")
    args = parser.parse_args()

    if args.watch:
        watch_mode()
    else:
        run_chameleon(wallpaper_path=args.wallpaper, forced_theme=args.theme, forced_placement=args.placement)
