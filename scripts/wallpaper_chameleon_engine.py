#!/usr/bin/env python3
"""
Jarvis X - Wallpaper Chameleon Engine
Analyzes active desktop wallpaper, extracts aesthetic accent color palette,
detects optimal negative-space screen placement, and hot-reloads JarvisChameleonClock.
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
    """Extract dominant aesthetic accent color, secondary hue, and text contrast."""
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
        # Filter for vibrant aesthetic accents (saturated, good brightness)
        if s >= 0.35 and 0.30 <= v <= 0.98:
            score = count * (s ** 1.8) * (v ** 0.6)
            candidates.append((score, (r, g, b), (h, s, v)))

    # Global luminance
    avg_lum = (0.299 * total_r + 0.587 * total_g + 0.114 * total_b) / (total_pixels * 255.0)

    if candidates:
        candidates.sort(reverse=True, key=lambda x: x[0])
        accent_r, accent_g, accent_b = candidates[0][1]
        h, s, v = candidates[0][2]
        # Generate complementary/secondary
        sec_h = (h + 0.08) % 1.0
        sec_r, sec_g, sec_b = [int(c * 255) for c in colorsys.hsv_to_rgb(sec_h, max(0.4, s * 0.9), min(1.0, v * 1.1))]
    else:
        # Monochromatic wallpaper
        if avg_lum < 0.5:
            accent_r, accent_g, accent_b = (56, 189, 248) # Cyan pop
            sec_r, sec_g, sec_b = (192, 132, 252)
        else:
            accent_r, accent_g, accent_b = (235, 70, 70) # Red pop
            sec_r, sec_g, sec_b = (50, 50, 60)

    # Determine contrast colors
    if avg_lum < 0.55:
        primary = "255,255,255,250"
        muted = "215,225,235,210"
        shadow = "0,0,0,180"
    else:
        primary = "20,25,35,250"
        muted = "60,65,75,210"
        shadow = "255,255,255,160"

    accent = f"{accent_r},{accent_g},{accent_b},255"
    secondary = f"{sec_r},{sec_g},{sec_b},240"

    return {
        "primary": primary,
        "accent": accent,
        "secondary": secondary,
        "muted": muted,
        "shadow": shadow,
        "avg_lum": avg_lum
    }

def analyze_placement(img, placement_pref="smart_center"):
    """
    Evaluates candidate screen zones for negative space (least visual clutter/edges).
    """
    w, h = img.size
    gray = img.convert('L')
    edges = gray.filter(ImageFilter.FIND_EDGES)

    # Candidate screen zones
    zones = {
        "CenterTop": {
            "bbox": (int(w * 0.28), int(h * 0.05), int(w * 0.72), int(h * 0.32)),
            "WindowX": "50%", "WindowY": "12%", "AnchorX": "50%", "AnchorY": "0%"
        },
        "CenterMid": {
            "bbox": (int(w * 0.25), int(h * 0.20), int(w * 0.75), int(h * 0.48)),
            "WindowX": "50%", "WindowY": "24%", "AnchorX": "50%", "AnchorY": "50%"
        },
        "UpperRight": {
            "bbox": (int(w * 0.60), int(h * 0.05), int(w * 0.95), int(h * 0.35)),
            "WindowX": "82%", "WindowY": "12%", "AnchorX": "50%", "AnchorY": "0%"
        },
        "UpperLeft": {
            "bbox": (int(w * 0.05), int(h * 0.05), int(w * 0.40), int(h * 0.35)),
            "WindowX": "18%", "WindowY": "12%", "AnchorX": "50%", "AnchorY": "0%"
        }
    }

    zone_scores = {}
    for zname, zinfo in zones.items():
        crop_edges = edges.crop(zinfo["bbox"])
        stat = ImageStat.Stat(crop_edges)
        edge_density = stat.mean[0]
        zone_scores[zname] = edge_density

    if placement_pref == "smart_center":
        # Prioritize CenterTop or CenterMid if relatively clean, else fallback to cleanest zone
        center_dens = min(zone_scores["CenterTop"], zone_scores["CenterMid"])
        cleanest = min(zone_scores, key=zone_scores.get)
        # If center is not overwhelmed by edges (e.g. within 2x of cleanest), keep center
        if zone_scores["CenterTop"] <= zone_scores["CenterMid"] * 1.3:
            best_name = "CenterTop"
        elif zone_scores["CenterMid"] <= zone_scores[cleanest] * 2.0:
            best_name = "CenterMid"
        else:
            best_name = cleanest
    elif placement_pref == "smart":
        best_name = min(zone_scores, key=zone_scores.get)
    else: # strict center
        best_name = "CenterTop" if zone_scores["CenterTop"] <= zone_scores["CenterMid"] else "CenterMid"

    selected = zones[best_name]
    selected["name"] = best_name
    selected["scores"] = zone_scores
    return selected

def update_skin_variables(palette, placement_name):
    """Write updated variables to Variables.inc in both target paths."""
    content = f"""[Variables]
Scale=1.1
ColorPrimary={palette['primary']}
ColorAccent={palette['accent']}
ColorSecondary={palette['secondary']}
ColorMuted={palette['muted']}
ColorShadow={palette['shadow']}
FontFaceDay=Anurati
FontFaceDate=Quicksand
FontFaceTime=Quicksand
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

def update_rainmeter_ini(placement, on_top=0):
    """Update Rainmeter.ini with JarvisChameleonClock placement and activate it."""
    if not os.path.exists(RAINMETER_INI):
        return

    with open(RAINMETER_INI, "r", encoding="utf-16", errors="ignore") as f:
        lines = f.readlines()

    new_lines = []
    in_target_section = False
    in_mond_section = False
    target_found = False

    for line in lines:
        sline = line.strip()
        if sline.startswith("[") and sline.endswith("]"):
            sec = sline[1:-1].strip()
            if sec.lower() in ("jarvischameleonclock", r"jarvischameleonclock\clock"):
                in_target_section = True
                target_found = True
                in_mond_section = False
                continue
            elif sec.lower() in ("mond", r"mond\clock"):
                in_mond_section = True
                in_target_section = False
                new_lines.append("[Mond\\Clock]\nActive=0\n")
                continue
            else:
                in_target_section = False
                in_mond_section = False

        if in_mond_section:
            if sline.startswith("Active="):
                pass
            continue

        if not in_target_section:
            new_lines.append(line)

    target_config = f"""
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
AlwaysOnTop={on_top}
"""
    new_lines.append(target_config)

    with open(RAINMETER_INI, "w", encoding="utf-16") as f:
        f.writelines(new_lines)
    print(f"[+] Updated Rainmeter.ini: [JarvisChameleonClock] Active=1 at {placement['WindowX']}, {placement['WindowY']}")

def reload_rainmeter():
    """Send refresh command or cold-start Rainmeter."""
    try:
        # Bang refresh
        subprocess.run([RAINMETER_EXE, "!Refresh", "JarvisChameleonClock"], check=False)
        subprocess.run([RAINMETER_EXE, "!RefreshApp"], check=False)
        print("[+] Sent !RefreshApp to Rainmeter")
    except Exception as e:
        print(f"[-] Could not send bang: {e}")

    # Verify Rainmeter is running
    out = subprocess.run(["tasklist"], capture_output=True, text=True, check=False)
    if "rainmeter" not in out.stdout.lower():
        print("[*] Rainmeter not running. Spawning via Task Scheduler interactive task...")
        subprocess.run(["schtasks", "/run", "/tn", "JarvisAestheticClock"], check=False)

def run_chameleon(wallpaper_path=None, pref="smart_center", on_top=0):
    wp = wallpaper_path or get_active_wallpaper()
    if not wp or not os.path.exists(wp):
        print("[-] Could not find active desktop wallpaper!")
        return False

    print(f"[*] Analyzing Wallpaper: {wp}")
    with Image.open(wp) as img:
        img_rgb = img.convert('RGB')
        palette = analyze_palette(img_rgb)
        placement = analyze_placement(img_rgb, placement_pref=pref)

    print(f"[*] Extracted Color Accent: {palette['accent']}")
    print(f"[*] Optimal Placement Zone: {placement['name']} (X: {placement['WindowX']}, Y: {placement['WindowY']})")

    update_skin_variables(palette, placement['name'])
    update_rainmeter_ini(placement, on_top=on_top)
    reload_rainmeter()
    print("[+] Chameleon sync completed successfully!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jarvis X Chameleon Clock Engine")
    parser.add_argument("--wallpaper", type=str, default=None, help="Explicit wallpaper path to analyze")
    parser.add_argument("--pref", type=str, default="smart_center", choices=["smart_center", "smart", "center"])
    parser.add_argument("--ontop", type=int, default=0, help="AlwaysOnTop setting (-2: Desktop, 0: Normal, 1: Top)")
    args = parser.parse_args()

    run_chameleon(wallpaper_path=args.wallpaper, pref=args.pref, on_top=args.ontop)
