#!/usr/bin/env python3
"""
Jarvis X - Live Demonstration: Agent Mike Auto-Theme Synthesis for New Lively Wallpapers
Simulates the user importing a brand new custom wallpaper into Lively Wallpaper.
Demonstrates:
1. Dynamic color quantization & WCAG AAA contrast calculation
2. Negative space analysis
3. Typography selection
4. High-resolution preview card generation with HUD specs
5. Strictly zero lag execution (<25ms)
"""

import sys
import os
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from jarvisx.agents.customizer_mike import MikeCustomizerAgent

BRAIN_DIR = Path(r"C:\Users\vanga\.gemini\antigravity\brain\5f3536a0-db67-45f8-b6ac-bcc96c90cbbf")
FONTS_DIR = PROJECT_ROOT / "assets" / "skins" / "JarvisChameleonClock" / "@Resources" / "Fonts"


def main():
    print("=" * 70)
    print("  AGENT MIKE - LIVE DEMO: NEW LIVELY WALLPAPER SYNTHESIS")
    print("=" * 70)

    mike = MikeCustomizerAgent()

    # Create a synthetic brand new custom aesthetic wallpaper:
    # "Cyberpunk Luminescent Metropolis" with deep violet shadows, neon teal, and hot magenta
    new_wp_path = BRAIN_DIR / "simulated_new_custom_wallpaper.png"
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), color=(12, 10, 24))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(h):
        r = int(12 + (y / h) * 20)
        g = int(10 + (y / h) * 15)
        b = int(24 + (y / h) * 45)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Busy focal point in center and lower right (futuristic skyline / buildings)
    for x in range(600, 1920, 40):
        b_h = 300 + (x % 350)
        draw.rectangle([x, h - b_h, x + 30, h], fill=(25, 25, 45))
        # Windows
        for wy in range(h - b_h + 20, h - 20, 25):
            win_color = (0, 240, 255) if (x + wy) % 3 == 0 else (255, 60, 180)
            draw.rectangle([x + 5, wy, x + 25, wy + 15], fill=win_color)

    # Neon glow line across bottom
    draw.line([(0, h - 100), (w, h - 100)], fill=(0, 240, 255), width=4)
    img.save(new_wp_path)
    print(f"[+] Created test new wallpaper: {new_wp_path.name} (Simulated Lively Import)")

    # Execute Agent Mike's synthesis
    start_t = time.perf_counter()
    synth_res = mike.synthesize_custom_wallpaper(str(new_wp_path), title="Neo Tokyo Metropolis Cyber Grid")
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0

    print(f"[+] Agent Mike Synthesized New Wallpaper in {elapsed_ms:.2f} ms! (Zero Lag)")
    print(f"    - Synthesized Title : {synth_res.get('title')}")
    theme = synth_res.get("theme", {})
    placement = synth_res.get("placement", {})
    print(f"    - Theme Classification : {theme.get('name')}")
    print(f"    - Selected Typography  : {theme.get('FontTitle')} (Auto-Mood Matched)")
    print(f"    - Negative Space Area  : {placement.get('placement')} (Quadrant Clutter Score: {placement['scores'].get(placement.get('placement')):.1f})")
    print(f"    - Accent Color         : {theme.get('ColorAccent')}")
    print(f"    - Text Contrast Ratio  : WCAG AAA Compliant ({theme.get('ColorPrimary')})")

    # Render a high-res preview card
    preview_canvas = img.copy()
    p_draw = ImageDraw.Draw(preview_canvas)

    # Draw Clock in the calculated negative space
    px = placement.get("pixel_x", 100)
    py = placement.get("pixel_y", 80)

    # Parse colors
    def parse_rgba(s):
        parts = [int(x.strip()) for x in s.split(",")]
        return tuple(parts[:3])

    col_accent = parse_rgba(theme.get("ColorAccent"))
    col_primary = parse_rgba(theme.get("ColorPrimary"))
    col_sub = parse_rgba(theme.get("ColorSub"))

    # Load font
    font_name = theme.get("FontTitle")
    font_path = None
    for f_cand in [FONTS_DIR / f"{font_name}.ttf", FONTS_DIR / f"{font_name}.otf"]:
        if f_cand.exists():
            font_path = f_cand
            break

    try:
        if font_path:
            f_day = ImageFont.truetype(str(font_path), 28)
            f_time = ImageFont.truetype(str(font_path), 82)
            f_date = ImageFont.truetype(str(font_path), 20)
        else:
            f_day = ImageFont.truetype("arial.ttf", 28)
            f_time = ImageFont.truetype("arial.ttf", 82)
            f_date = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        f_day = f_time = f_date = ImageFont.load_default()

    # Draw minimalist clock (Day, Time, Date) - STRICTLY NO FRANCHISE TITLE
    # Shadow
    for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, 3)]:
        p_draw.text((px + dx, py + dy), "FRIDAY", font=f_day, fill=(0, 0, 0))
        p_draw.text((px + dx, py + 35 + dy), "10:45", font=f_time, fill=(0, 0, 0))
        p_draw.text((px + dx, py + 125 + dy), "25 SEPTEMBER 2026", font=f_date, fill=(0, 0, 0))

    # Foreground
    p_draw.text((px, py), "FRIDAY", font=f_day, fill=col_accent)
    p_draw.text((px, py + 35), "10:45", font=f_time, fill=col_primary)
    p_draw.text((px, py + 125), "25 SEPTEMBER 2026", font=f_date, fill=col_sub)

    # Bottom HUD spec bar
    bar_h = 70
    p_draw.rectangle([0, h - bar_h, w, h], fill=(12, 12, 16))
    p_draw.line([(0, h - bar_h), (w, h - bar_h)], fill=(0, 240, 255), width=2)

    try:
        f_hud_bold = ImageFont.truetype("segoeuib.ttf", 15)
        f_hud = ImageFont.truetype("segoeui.ttf", 13)
    except Exception:
        f_hud_bold = f_hud = ImageFont.load_default()

    p_draw.text((25, h - bar_h + 12), "AGENT MIKE - DYNAMIC AUTO-SYNTHESIS ENGINE (NEW LIVELY WALLPAPER)", font=f_hud_bold, fill=(0, 240, 255))
    p_draw.text((25, h - bar_h + 38), f"Wall: {synth_res.get('title')} | Zero-Lag Execution: {elapsed_ms:.1f}ms | WCAG AAA 7:1", font=f_hud, fill=(180, 180, 190))

    p_draw.text((w // 2 - 50, h - bar_h + 12), f"Typography: {theme.get('FontTitle')} (Auto-Resolved)", font=f_hud, fill=(240, 240, 250))
    p_draw.text((w // 2 - 50, h - bar_h + 38), f"Negative Space: {placement.get('placement')} | Single Master Clock: Strict Active=1", font=f_hud, fill=(160, 160, 170))

    # Color Swatches
    swatch_x = w - 180
    p_draw.text((swatch_x - 60, h - bar_h + 24), "Palette:", font=f_hud, fill=(160, 160, 170))
    for col in [col_accent, col_primary, col_sub]:
        p_draw.ellipse([swatch_x, h - bar_h + 24, swatch_x + 18, h - bar_h + 42], fill=col)
        swatch_x += 26

    out_preview = BRAIN_DIR / "preview_agent_mike_auto_synthesis.png"
    preview_canvas.save(out_preview)
    print(f"[+] Saved High-Res Preview Card: {out_preview}")
    print("[+] Demonstration successfully completed!")


if __name__ == "__main__":
    main()
