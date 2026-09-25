#!/usr/bin/env python3
"""
Jarvis X - Comprehensive Wallpaper Preview & Theme Specification Generator
Generates full 1080p/1200p wallpaper previews with exact font rendering,
embedded symbols, color swatches, and screen placements.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
ARTIFACTS_DIR = r"C:\Users\vanga\.gemini\antigravity\brain\5f3536a0-db67-45f8-b6ac-bcc96c90cbbf"
FONTS_DIR = os.path.join(PROJECT_DIR, "assets", "skins", "JarvisChameleonClock", "@Resources", "Fonts")

sys.path.insert(0, PROJECT_DIR)
from scripts.wallpaper_chameleon_engine import THEMES, analyze_negative_space

WALLPAPER_SPECS = [
    {
        "key": "one_piece",
        "title": "One Piece (Gear 5 Sun God Nika & Straw Hat Pirates)",
        "wallpaper": os.path.join(PROJECT_DIR, "assets", "wallpapers", "one_piece_gear5_moon.jpg"),
        "font_file": "OnePiece_TitleFont.ttf",
        "font_name": "ONE PIECE",
        "symbols": "Luffy Silhouette in 'I', Straw Hat Jolly Roger Skull in '0', Anchor in 'E', Anchor Hook in '5'",
        "accent_hex": "#3A92E8",
        "primary_hex": "#FFFFFF",
        "sub_hex": "#FFD71E",
        "placement_pref": "UpperLeft"
    },
    {
        "key": "batman",
        "title": "The Batman (Gotham Noir Vengeance)",
        "wallpaper": os.path.join(PROJECT_DIR, "assets", "wallpapers", "the_batman_2022.png"),
        "font_file": "BatmanForever.ttf",
        "font_name": "BatmanForeverAlternate",
        "symbols": "Bat Wings on 'M', 'F', 'R', 'D', 'Y' & Sharp Batarang Cuts on Numerals '10:45'",
        "accent_hex": "#E11923",
        "primary_hex": "#FFFFFF",
        "sub_hex": "#B4B4BE",
        "placement_pref": "UpperLeft"
    },
    {
        "key": "naruto",
        "title": "Naruto Shippuden (Kurama Nine-Tails & Sage Mode)",
        "wallpaper": os.path.join(PROJECT_DIR, "assets", "wallpapers", "naruto_4k_lockscreen.jpg"),
        "font_file": "njnaruto.ttf",
        "font_name": "Ninja Naruto",
        "symbols": "Kunai Slash Numerals, Shinobi Brush Lettering & Uzumaki Spiral Symbol '@'",
        "accent_hex": "#FF820A",
        "primary_hex": "#FFFFFF",
        "sub_hex": "#FACC15",
        "placement_pref": "UpperLeft"
    },
    {
        "key": "rdr2",
        "title": "Red Dead Redemption 2 (Arthur Morgan & Van der Linde Gang)",
        "wallpaper": r"C:\Users\vanga\Pictures\AestheticThemes\RDR2_Aesthetic.jpg",
        "font_file": "chinese rocks rg.otf",
        "font_name": "Chinese Rocks",
        "symbols": "Weathered Frontier Woodcut Lettering & Authentic Rockstar Outlaw Typography",
        "accent_hex": "#E12D23",
        "primary_hex": "#FAF5EB",
        "sub_hex": "#D2A05A",
        "placement_pref": "UpperLeft"
    },
    {
        "key": "ghost_cod",
        "title": "Call of Duty: Modern Warfare (Simon 'Ghost' Riley / TF141)",
        "wallpaper": os.path.join(PROJECT_DIR, "assets", "wallpapers", "ghost_cod_4k.png"),
        "font_file": "AgencyFB.ttf",
        "font_name": "Agency FB Bold",
        "symbols": "Military Comms HUD Typography, Angular Tactical Cuts & NVG Crimson Targeting",
        "accent_hex": "#EB1E28",
        "primary_hex": "#FAF5EB",
        "sub_hex": "#B0B4C0",
        "placement_pref": "UpperLeft"
    },
    {
        "key": "samurai",
        "title": "Ghost of Tsushima / Samurai (Katana Bushido & Autumn Maple)",
        "wallpaper": os.path.join(PROJECT_DIR, "assets", "wallpapers", "kyoto_pagoda_twilight.jpg"),
        "font_file": "Shojumaru.ttf",
        "font_name": "Shojumaru",
        "symbols": "Curved Katana Blade Edge Cuts on Numerals & Sword Crossbar Lettering",
        "accent_hex": "#FF2D37",
        "primary_hex": "#FAF5EE",
        "sub_hex": "#B4B4C0",
        "placement_pref": "UpperLeft"
    },
    {
        "key": "minecraft",
        "title": "Minecraft (Shaders Landscape & Emerald XP Voxel)",
        "wallpaper": os.path.join(PROJECT_DIR, "assets", "wallpapers", "minecraft_4k_wallpaper.jpg"),
        "font_file": "Minecraft.ttf",
        "font_name": "Minecraft (Mojangles Pixel)",
        "symbols": "Authentic In-Game Pixel Numerals, Voxel Lettering & Cracked Block Texture (Minecrafter Alt)",
        "accent_hex": "#55FF55",
        "primary_hex": "#FFFFFF",
        "sub_hex": "#FFAA00",
        "placement_pref": "UpperLeft"
    }
]

def parse_col(col_str):
    parts = [int(p.strip()) for p in col_str.split(",")]
    return tuple(parts)

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def render_preview(spec):
    wp_path = spec["wallpaper"]
    theme_key = spec["key"]
    theme_cfg = THEMES[theme_key]

    target_w, target_h = 1920, 1080

    if os.path.exists(wp_path):
        bg = Image.open(wp_path).convert("RGBA")
        # Resize preserving aspect ratio (crop to 1920x1080)
        scale = max(target_w / bg.width, target_h / bg.height)
        new_w = int(bg.width * scale)
        new_h = int(bg.height * scale)
        bg = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)
        # Center crop
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        bg = bg.crop((left, top, left + target_w, top + target_h))
    else:
        bg = Image.new("RGBA", (target_w, target_h), (20, 22, 28, 255))

    placement = analyze_negative_space(bg, preferred_placement=spec["placement_pref"])
    
    # Calculate screen coordinates based on placement
    if placement["name"] == "UpperRight":
        clk_x = int(target_w * 0.70)
        clk_y = int(target_h * 0.06)
    elif placement["name"] == "CenterTop":
        clk_x = int(target_w * 0.38)
        clk_y = int(target_h * 0.06)
    else: # UpperLeft default
        clk_x = int(target_w * 0.05)
        clk_y = int(target_h * 0.06)

    # Load Fonts
    font_path = os.path.join(FONTS_DIR, spec["font_file"])
    try:
        font_day = ImageFont.truetype(font_path, 32)
        font_time = ImageFont.truetype(font_path, 98)
        font_date = ImageFont.truetype(font_path, 22)
    except Exception:
        font_day = ImageFont.load_default()
        font_time = ImageFont.load_default()
        font_date = ImageFont.load_default()

    accent_col = parse_col(theme_cfg["ColorAccent"])
    primary_col = parse_col(theme_cfg["ColorPrimary"])
    muted_col = parse_col(theme_cfg["ColorMuted"])
    shadow_col = parse_col(theme_cfg["ColorShadow"])
    effect = theme_cfg.get("StringEffect", "Shadow")
    stroke_w = 2 if effect == "Border" else 1

    draw = ImageDraw.Draw(bg)

    # 1. Day of Week
    draw.text((clk_x, clk_y), "FRIDAY", font=font_day, fill=accent_col, stroke_width=stroke_w, stroke_fill=shadow_col)

    # 2. Main Time
    draw.text((clk_x, clk_y + 44), "10:45", font=font_time, fill=primary_col, stroke_width=stroke_w + 1, stroke_fill=shadow_col)

    # 3. Full Date
    draw.text((clk_x + 2, clk_y + 168), "25 SEPTEMBER 2026", font=font_date, fill=muted_col, stroke_width=1, stroke_fill=shadow_col)

    # --- Spec HUD Info Banner at the Bottom ---
    hud_h = 80
    hud_y = target_h - hud_h
    # Semi-transparent dark frosted glass bar
    hud_overlay = Image.new("RGBA", (target_w, hud_h), (10, 12, 16, 235))
    bg.paste(hud_overlay, (0, hud_y), hud_overlay)

    hud_draw = ImageDraw.Draw(bg)
    try:
        hud_font_title = ImageFont.truetype("segoeuib.ttf", 20)
        hud_font_body = ImageFont.truetype("segoeui.ttf", 15)
        hud_font_code = ImageFont.truetype("consola.ttf", 14)
    except Exception:
        hud_font_title = ImageFont.load_default()
        hud_font_body = ImageFont.load_default()
        hud_font_code = ImageFont.load_default()

    # Left: Title and Symbols
    hud_draw.text((30, hud_y + 12), spec["title"].upper(), font=hud_font_title, fill=parse_col(theme_cfg["ColorAccent"]))
    hud_draw.text((30, hud_y + 42), f"Symbols: {spec['symbols']}", font=hud_font_body, fill=(210, 215, 225, 255))

    # Center-Right: Typography & Placement
    info_x = int(target_w * 0.58)
    hud_draw.text((info_x, hud_y + 14), f"Typography: {spec['font_name']} ({spec['font_file']})", font=hud_font_body, fill=(240, 245, 255, 255))
    hud_draw.text((info_x, hud_y + 42), f"Placement: {placement['name']} ({placement['WindowX']}, {placement['WindowY']} on Screen 1)", font=hud_font_body, fill=(180, 190, 205, 255))

    # Right: Palette Swatches
    swatch_x = target_w - 220
    hud_draw.text((swatch_x, hud_y + 14), "Palette:", font=hud_font_body, fill=(200, 200, 200, 255))
    
    # Draw colored circles
    swatches = [
        (accent_col, spec["accent_hex"]),
        (primary_col, spec["primary_hex"]),
        (parse_col(theme_cfg["ColorSub"]), spec["sub_hex"])
    ]
    sx = swatch_x + 65
    for scol, shex in swatches:
        hud_draw.ellipse((sx, hud_y + 12, sx + 20, hud_y + 32), fill=scol, outline=(255, 255, 255, 120))
        sx += 30

    hud_draw.text((swatch_x, hud_y + 42), f"{spec['accent_hex']} | {spec['primary_hex']}", font=hud_font_code, fill=(160, 170, 185, 255))

    out_file = os.path.join(ARTIFACTS_DIR, f"preview_wallpaper_{theme_key}.png")
    bg.save(out_file, "PNG")
    print(f"[+] Saved: {out_file}")
    return out_file

def main():
    print("=" * 70)
    print("  JARVIS X - WALLPAPER PREVIEW GENERATOR")
    print("=" * 70)
    out_files = []
    for spec in WALLPAPER_SPECS:
        print(f"[*] Rendering wallpaper preview for: {spec['title']}...")
        out_f = render_preview(spec)
        out_files.append((spec, out_f))

    print(f"\n[+] Successfully generated all {len(out_files)} wallpaper preview cards!")

if __name__ == "__main__":
    main()
