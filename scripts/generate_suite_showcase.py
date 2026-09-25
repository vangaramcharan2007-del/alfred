#!/usr/bin/env python3
"""
Generates visual presentation cards for the Jarvis X Chameleon Clock & Visualizer Suite.
Shows the enlarged clock and audio visualizer in Boss's requested top placements.
"""

import os
import sys
import glob
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from jarvisx.agents.customizer_mike import PRESET_THEMES

ARTIFACT_DIR = Path(r"C:\Users\vanga\.gemini\antigravity\brain\5f3536a0-db67-45f8-b6ac-bcc96c90cbbf")
FONTS_DIR = PROJECT_ROOT / "assets" / "fonts"


def get_font(font_name: str, size: int):
    # Try local fonts dir first
    matches = list(FONTS_DIR.glob(f"*{font_name}*"))
    if matches:
        try:
            return ImageFont.truetype(str(matches[0]), size)
        except Exception:
            pass
    # Try Windows fonts
    win_font_dir = Path("C:/Windows/Fonts")
    for f in win_font_dir.glob("*.ttf"):
        if font_name.lower() in f.stem.lower():
            try:
                return ImageFont.truetype(str(f), size)
            except Exception:
                pass
    # Fallbacks
    for fb in ["arialbd.ttf", "segoeui.ttf", "arial.ttf"]:
        p = win_font_dir / fb
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_suite_card(wallpaper_path: str, theme_key: str, output_name: str):
    if not os.path.exists(wallpaper_path):
        return None

    img = Image.open(wallpaper_path).convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    theme = PRESET_THEMES.get(theme_key, PRESET_THEMES["one_piece"])
    placement = theme.get("PrefPlacement", "UpperLeft")

    # Colors
    def parse_col(s):
        parts = [int(p.strip()) for p in s.split(",")[:4]]
        return tuple(parts)

    accent_col = parse_col(theme.get("ColorAccent", "255, 45, 55, 255"))
    primary_col = parse_col(theme.get("ColorPrimary", "255, 255, 255, 255"))
    sub_col = parse_col(theme.get("ColorSub", "229, 168, 75, 255"))

    # Fonts
    font_title = get_font(theme.get("FontTitle", "Shojumaru"), int(28 * 1.4))
    font_time = get_font(theme.get("FontTime", "Shojumaru"), int(96 * 1.45))
    font_day = get_font(theme.get("FontDate", "Segoe UI Semibold"), int(24 * 1.4))
    font_date = get_font(theme.get("FontDate", "Segoe UI Semibold"), int(16 * 1.4))

    # Positions
    if placement == "TopCenter":
        cx = int(w * 0.50)
        cy = 50
        align = "center"
        vx = int(w * 0.50) - 250
        vy = cy + 240
    else:  # UpperLeft
        cx = 70
        cy = 50
        align = "left"
        vx = 70
        vy = cy + 240

    # Draw Title
    title_text = theme.get("name").split("(")[0].strip().upper()
    draw.text((cx, cy), title_text, fill=accent_col, font=font_title, anchor="ma" if align == "center" else "la")

    # Draw Clock Time
    time_text = "07 : 30"
    draw.text((cx, cy + 38), time_text, fill=primary_col, font=font_time, anchor="ma" if align == "center" else "la")

    # Draw Day & Date
    day_text = "FRIDAY"
    date_text = "SEPTEMBER 25, 2026"
    draw.text((cx, cy + 175), day_text, fill=sub_col, font=font_day, anchor="ma" if align == "center" else "la")
    draw.text((cx, cy + 210), date_text, fill=primary_col, font=font_date, anchor="ma" if align == "center" else "la")

    # Draw Chameleon Audio Visualizer (16 bars)
    bar_w = 12
    bar_gap = 4
    import math
    for i in range(16):
        # Simulated dynamic frequency curve
        height = int(12 + 32 * abs(math.sin(i * 0.45 + 0.8)))
        bx = vx + i * (bar_w + bar_gap)
        by = vy + (48 - height)
        # Background bar
        draw.rectangle([bx, vy, bx + bar_w, vy + 48], fill=(0, 0, 0, 70))
        # Active audio bar with accent color
        draw.rectangle([bx, by, bx + bar_w, vy + 48], fill=accent_col)

    # Visualizer NowPlaying text
    font_media_title = get_font("Segoe UI", 14)
    font_media_sub = get_font("Segoe UI", 11)
    draw.text((vx + 16 * (bar_w + bar_gap) + 12, vy + 6), "NOW PLAYING: THEME SOUNDTRACK", fill=primary_col, font=font_media_title)
    draw.text((vx + 16 * (bar_w + bar_gap) + 12, vy + 26), f"Jarvis X Chameleon Audio HUD  |  DWM Accent: #{accent_col[0]:02X}{accent_col[1]:02X}{accent_col[2]:02X}", fill=sub_col, font=font_media_sub)

    # Simulated Taskbar Accent Stripe at bottom
    tb_h = 42
    draw.rectangle([0, h - tb_h, w, h], fill=(20, 20, 25, 230))
    draw.line([0, h - tb_h, w, h - tb_h], fill=accent_col, width=3)
    font_tb = get_font("Segoe UI", 12)
    draw.text((w // 2, h - tb_h + 12), f"WINDOWS 11 DWM TASKBAR SYNCHRONIZED [ACCENT COLOR #{accent_col[0]:02X}{accent_col[1]:02X}{accent_col[2]:02X}]", fill=primary_col, font=font_tb, anchor="mm")

    # Composite
    final_img = Image.alpha_composite(img, overlay).convert("RGB")
    out_path = ARTIFACT_DIR / output_name
    final_img.save(out_path, quality=92)
    print(f"[+] Rendered preview card: {out_path}")
    return out_path


def main():
    root = Path(r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper\Library")
    search_dirs = [root / "wallpapers", root / "SaveData" / "wptmp"]
    
    # Showcase wallpapers:
    showcases = [
        ("spiderman", "TopCenter", "preview_suite_spiderman.png"),
        ("samurai", "UpperLeft", "preview_suite_samurai.png"),
        ("one_piece", "UpperLeft", "preview_suite_onepiece.png"),
        ("rdr2", "UpperLeft", "preview_suite_rdr2.png"),
        ("ghost_cod", "UpperLeft", "preview_suite_cod.png"),
    ]

    for theme_key, _, out_file in showcases:
        preset = PRESET_THEMES[theme_key]
        found_wp = None
        for base in search_dirs:
            if not base.exists():
                continue
            for wp_dir in base.glob("*"):
                if not wp_dir.is_dir():
                    continue
                combined = wp_dir.name.lower()
                info_file = wp_dir / "LivelyInfo.json"
                if info_file.exists():
                    try:
                        combined += " " + info_file.read_text(encoding="utf-8", errors="ignore").lower()
                    except Exception:
                        pass
                if any(k in combined for k in preset["keywords"]):
                    # find thumbnail or image
                    for ext in ["*.jpg", "*.png", "*.jpeg"]:
                        imgs = list(wp_dir.glob(ext))
                        if imgs:
                            found_wp = str(imgs[0])
                            break
                if found_wp:
                    break
            if found_wp:
                break
        
        if found_wp:
            render_suite_card(found_wp, theme_key, out_file)
        else:
            print(f"[-] Could not find wallpaper matching theme: {theme_key}")


if __name__ == "__main__":
    main()
