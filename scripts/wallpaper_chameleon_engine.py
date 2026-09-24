#!/usr/bin/env python3
"""
Jarvis X - Wallpaper Chameleon Engine v3.0
Analyzes desktop wallpaper, extracts aesthetic accent color palette,
detects optimal negative-space placement (Top-Left / Top-Right / High-Center),
and hot-reloads the single unified JarvisChameleonClock with zero lag.
"""

import os
import sys
import argparse
import colorsys
import subprocess
import winreg
from PIL import Image, ImageFilter, ImageStat

RAINMETER_EXE = r"C:\Program Files\Rainmeter\Rainmeter.exe"
SKINS_DIR = r"C:\Users\vanga\OneDrive\Documents\Rainmeter\Skins\JarvisChameleonClock"
PROJECT_SKIN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "skins", "JarvisChameleonClock")
RAINMETER_INI = os.path.expanduser(r"~\AppData\Roaming\Rainmeter\Rainmeter.ini")

def get_active_wallpaper():
    """Locate current active Windows wallpaper image."""
    transcoded = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Themes\TranscodedWallpaper")
    if os.path.exists(transcoded) and os.path.getsize(transcoded) > 0:
        return transcoded

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop")
        val, _ = winreg.QueryValueEx(key, "WallPaper")
        winreg.CloseKey(key)
        if os.path.exists(val):
            return val
    except Exception:
        pass
    return None

def analyze_palette(img):
    """
    Extracts the dominant vibrant aesthetic accent color, secondary hue,
    and high-contrast text colors from the wallpaper.
    """
    thumb = img.resize((120, 120))
    colors = thumb.getcolors(maxcolors=20000) or []

    candidates = []
    total_r, total_g, total_b = 0, 0, 0
    total_pixels = max(1, sum(c[0] for c in colors))

    for count, (r, g, b) in colors:
        total_r += r * count
        total_g += g * count
        total_b += b * count
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        # Saturated aesthetic accents (skip washed-out whites/grays or pitch black)
        if s >= 0.35 and 0.35 <= v <= 0.98:
            score = count * (s ** 1.8) * (v ** 0.6)
            candidates.append((score, (r, g, b), (h, s, v)))

    # Global luminance
    avg_lum = (0.299 * total_r + 0.587 * total_g + 0.114 * total_b) / (total_pixels * 255.0)

    if candidates:
        candidates.sort(reverse=True, key=lambda x: x[0])
        accent_r, accent_g, accent_b = candidates[0][1]
        h, s, v = candidates[0][2]
        # Generate secondary color (slight hue shift)
        sec_h = (h + 0.08) % 1.0
        sec_r, sec_g, sec_b = [int(c * 255) for c in colorsys.hsv_to_rgb(sec_h, max(0.4, s * 0.9), min(1.0, v * 1.1))]
    else:
        # Default aesthetic gold/orange accent if monochromatic
        accent_r, accent_g, accent_b = (255, 140, 20)
        sec_r, sec_g, sec_b = (255, 195, 50)

    # High-legibility text contrast
    if avg_lum < 0.65:
        primary = "255,255,255,245"
        muted = "235,225,200,200"
        shadow = "0,0,0,220"
    else:
        primary = "25,30,40,245"
        muted = "70,75,85,210"
        shadow = "255,255,255,180"

    accent = f"{accent_r},{accent_g},{accent_b},255"
    secondary = f"{sec_r},{sec_g},{sec_b},255"

    return {
        "primary": primary,
        "accent": accent,
        "secondary": secondary,
        "muted": muted,
        "shadow": shadow,
        "avg_lum": avg_lum
    }

def analyze_placement(img):
    """
    Evaluates where the open negative space is (UpperLeft vs UpperRight vs CenterTop).
    Avoids putting the clock on character faces, heads, or busy artwork.
    """
    w, h = img.size
    gray = img.convert('L')
    edges = gray.filter(ImageFilter.FIND_EDGES)

    # Candidate aesthetic zones
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
            "bbox": (int(w * 0.30), int(h * 0.03), int(w * 0.70), int(h * 0.28)),
            "WindowX": "50%", "WindowY": "6%", "AnchorX": "50%", "AnchorY": "0%"
        }
    }

    zone_scores = {}
    for zname, zinfo in zones.items():
        crop_edges = edges.crop(zinfo["bbox"])
        stat = ImageStat.Stat(crop_edges)
        edge_density = stat.mean[0]
        zone_scores[zname] = edge_density

    # Default preference: UpperLeft is the gold standard for battlestations
    # Only shift to UpperRight if UpperLeft has high clutter (e.g., character is on the left)
    if zone_scores["UpperLeft"] <= zone_scores["UpperRight"] * 1.4:
        best_name = "UpperLeft"
    elif zone_scores["UpperRight"] < zone_scores["UpperLeft"]:
        best_name = "UpperRight"
    else:
        best_name = "CenterTop"

    selected = zones[best_name]
    selected["name"] = best_name
    selected["scores"] = zone_scores
    return selected

def update_skin_variables(palette, placement_name):
    """Write updated variables to Variables.inc in both target paths."""
    content = f"""[Variables]
FontName=Segoe UI Light
FontBold=Segoe UI Semibold
Scale=1.0
ColorPrimary={palette['primary']}
ColorAccent={palette['accent']}
ColorSub={palette['secondary']}
ColorMuted={palette['muted']}
ColorShadow={palette['shadow']}
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
    print(f"[+] Updated Variables.inc with Accent: {palette['accent']} in {placement_name}")

def update_rainmeter_ini(placement):
    """
    Ensure ONLY [JarvisChameleonClock] is Active=1.
    All duplicate/old clocks are deactivated.
    """
    if not os.path.exists(RAINMETER_INI):
        return

    clean_ini = f"""[Rainmeter]
Logging=1
SkinPath=C:\\Users\\vanga\\OneDrive\\Documents\\Rainmeter\\Skins\\

[JarvisChameleonClock]
Active=1
WindowX={placement['WindowX']}
WindowY={placement['WindowY']}
AnchorX={placement['AnchorX']}
AnchorY={placement['AnchorY']}
ClickThrough=0
Draggable=1
SnapEdges=1
KeepOnScreen=1
AlwaysOnTop=0

[NarutoSage\\Clock]
Active=0

[Gear5Nika\\Clock]
Active=0

[GhostMinimal\\Clock]
Active=0

[Mond\\Clock]
Active=0

[illustro\\Clock]
Active=0

[illustro\\Disk]
Active=0

[illustro\\System]
Active=0

[illustro\\Welcome]
Active=0

[ArthurMorganRDR\\Clock]
Active=0
"""
    with open(RAINMETER_INI, "w", encoding="utf-16") as f:
        f.write(clean_ini)
    print(f"[+] Updated Rainmeter.ini: [JarvisChameleonClock] Active=1 at {placement['WindowX']}, {placement['WindowY']} (All duplicates deactivated)")

def reload_rainmeter():
    """Send refresh command to Rainmeter."""
    try:
        subprocess.run([RAINMETER_EXE, "!Refresh", "JarvisChameleonClock"], check=False)
        subprocess.run([RAINMETER_EXE, "!RefreshApp"], check=False)
        print("[+] Sent !Refresh to Rainmeter")
    except Exception as e:
        print(f"[-] Could not send bang: {e}")

def run_chameleon(wallpaper_path=None):
    wp = wallpaper_path or get_active_wallpaper()
    if not wp or not os.path.exists(wp):
        print("[-] Could not find active desktop wallpaper!")
        return False

    print(f"[*] Analyzing Wallpaper: {wp}")
    with Image.open(wp) as img:
        img_rgb = img.convert('RGB')
        palette = analyze_palette(img_rgb)
        placement = analyze_placement(img_rgb)

    print(f"[*] Extracted Color Accent: {palette['accent']}")
    print(f"[*] Optimal Placement Zone: {placement['name']} (X: {placement['WindowX']}, Y: {placement['WindowY']})")

    update_skin_variables(palette, placement['name'])
    update_rainmeter_ini(placement)
    reload_rainmeter()
    print("[+] Chameleon sync completed successfully with 0 duplicate clocks!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jarvis X Chameleon Clock Engine")
    parser.add_argument("--wallpaper", type=str, default=None, help="Explicit wallpaper path to analyze")
    args = parser.parse_args()

    run_chameleon(wallpaper_path=args.wallpaper)
