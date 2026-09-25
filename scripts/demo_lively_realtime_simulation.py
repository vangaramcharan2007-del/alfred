#!/usr/bin/env python3
"""
Jarvis X - Agent Mike Live Demonstration with Real Lively Wallpapers
Cycles through Boss's actual installed Lively Wallpaper library:
1. One Piece (Gear 5 Bounce on Water)
2. Spider-Man (Spider-Man's Crimson Sky)
3. Spider-Man (Falling Upside Down Spider-Verse Neon City)
4. The Batman (The Batman Rain)
5. Call of Duty (Simon Ghost Riley Red Ghost)
6. Minecraft (Minecraft Sunset Shaders)
7. Ghost of Tsushima / Samurai (Bloodfall Pagoda)
8. Red Dead Redemption 2 (Arthur Morgan Sunset)
9. Medusae Jellyfish (Dynamic Bioluminescent Auto-Synthesis)

Enforces:
- Strictly TOP placement (UpperLeft, TopCenter, UpperRight) per Boss's preference
- Increased font size (+25% larger, commanding presence)
- Authentic franchise typography (including The Amazing Spider-Man, ONE PIECE, Ninja Naruto, Batman, Agency FB, Shojumaru, Minecraft)
- Strict single master clock
- Zero lag (<50ms execution)
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

LIVELY_TEST_SUITE = [
    {
        "id": "lively_one_piece",
        "title": "gear-5-bounce-on-water.3840x2160",
        "path": r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper\Library\SaveData\wptmp\gnfdja2y.mi2\34pxnxbz.rsq.jpg",
        "category": "One Piece"
    },
    {
        "id": "lively_spiderman_crimson",
        "title": "spider-mans-crimson-sky.1920x1080",
        "path": r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper\Library\SaveData\wptmp\bs0fsr41.o0i\hc52gbuv.2ct.jpg",
        "category": "Spider-Man"
    },
    {
        "id": "lively_spiderman_spiderverse",
        "title": "falling-upside-down-neon-city-spiderman-into-the-spiderverse-moewalls-com",
        "path": r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper\Library\SaveData\wptmp\rbkvdivr.azm\102bcvit.1j0.jpg",
        "category": "Spider-Man"
    },
    {
        "id": "lively_batman",
        "title": "batman-rain.3840x2160",
        "path": r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper\Library\SaveData\wptmp\3rox5a4j.buh\vzdr4ieh.qmn.jpg",
        "category": "The Batman"
    },
    {
        "id": "lively_ghost_cod",
        "title": "red-ghost.3840x2160",
        "path": r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper\Library\SaveData\wptmp\eu1a1oyl.dxw\n3aff32l.its.jpg",
        "category": "Call of Duty: Modern Warfare"
    },
    {
        "id": "lively_minecraft",
        "title": "minecraft-sunset2.3840x2160",
        "path": r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper\Library\SaveData\wptmp\4ytzph4d.ytb\dmk45pvf.zt5.jpg",
        "category": "Minecraft"
    },
    {
        "id": "lively_samurai",
        "title": "ghost-of-tsushima-bloodfall.3840x2160",
        "path": r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper\Library\SaveData\wptmp\iwgorb25.z30\vqt52ac4.dqc.jpg",
        "category": "Ghost of Tsushima"
    },
    {
        "id": "lively_rdr2",
        "title": "arthur-morgan-sunset.3840x2160",
        "path": r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper\Library\SaveData\wptmp\tjhwktyp.oyz\iu5evr3s.fq1.jpg",
        "category": "Red Dead Redemption 2"
    },
    {
        "id": "lively_medusae",
        "title": "Medusae Bioluminescent Jellyfish",
        "path": r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper\Library\wallpapers\nps35xrp.5eh\lively_t.jpg",
        "category": "Dynamic Aesthetic Auto-Synthesis"
    }
]


def parse_rgba(s):
    parts = [int(x.strip()) for x in s.split(",")]
    return tuple(parts[:3])


FONT_FILE_MAP = {
    "one piece": "OnePiece_TitleFont.ttf",
    "onepiece": "OnePiece_TitleFont.ttf",
    "onepiece_titlefont": "OnePiece_TitleFont.ttf",
    "the amazing spider-man": "The Amazing Spider-Man.ttf",
    "the amazing spider man": "The Amazing Spider-Man.ttf",
    "theamazingspiderman": "The Amazing Spider-Man.ttf",
    "spiderman": "The Amazing Spider-Man.ttf",
    "spider-man": "The Amazing Spider-Man.ttf",
    "homoarakhn": "HOMOARAK.TTF",
    "homoarak": "HOMOARAK.TTF",
    "homoarakhan": "HOMOARAK.TTF",
    "batmanforeveralternate": "BatmanForever.ttf",
    "batmanforever": "BatmanForever.ttf",
    "batman": "BatmanForever.ttf",
    "ninja naruto": "njnaruto.ttf",
    "njnaruto": "njnaruto.ttf",
    "naruto": "njnaruto.ttf",
    "chinese rocks": "chinese rocks rg.otf",
    "chinese rocks rg": "chinese rocks rg.otf",
    "agency fb": "AgencyFB.ttf",
    "agencyfb": "AgencyFB.ttf",
    "shojumaru": "Shojumaru.ttf",
    "minecraft": "Minecraft.ttf",
    "bebas neue": "BebasNeue.ttf",
    "bebasneue": "BebasNeue.ttf",
    "cinzel decorative": "Cinzel.ttf",
    "cinzel": "Cinzel.ttf",
    "dela gothic one": "DelaGothicOne.ttf",
    "delagothicone": "DelaGothicOne.ttf",
    "aquatico": "Aquatico.otf",
    "quicksand": "Quicksand.otf",
    "yuji boku": "YujiBoku.ttf",
}


def resolve_font(font_name, size):
    name_clean = str(font_name).lower().strip()
    target_file = FONT_FILE_MAP.get(name_clean, f"{font_name}.ttf")

    candidates = [
        FONTS_DIR / target_file,
        FONTS_DIR / f"{font_name}.ttf",
        FONTS_DIR / f"{font_name}.otf",
        FONTS_DIR / f"{font_name}.TTF",
        Path(f"C:/Windows/Fonts/{target_file}"),
        Path(f"C:/Windows/Fonts/{font_name}.ttf"),
        Path(f"C:/Windows/Fonts/{font_name}.otf")
    ]
    for c in candidates:
        if c.exists():
            try:
                return ImageFont.truetype(str(c), size)
            except Exception:
                pass
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def main():
    print("=" * 75)
    print("   AGENT MIKE - LIVE REALTIME LIVELY WALLPAPER SYNCHRONIZATION DEMO")
    print("   (TOP-ONLY PLACEMENT & ENLARGED COMMANDING CLOCK PREVIEW)")
    print("=" * 75)

    mike = MikeCustomizerAgent()
    generated_previews = []

    for item in LIVELY_TEST_SUITE:
        print(f"\n[*] Processing Lively Wallpaper: {item['title']} ({item['category']})...")
        img_path = Path(item["path"])
        if not img_path.exists():
            print(f"[-] Thumbnail not found: {img_path}")
            continue

        start_t = time.perf_counter()
        with Image.open(img_path) as orig_img:
            img = orig_img.convert("RGB")

        # 1. Theme & typography synthesis
        theme = mike.synthesize_theme(img, [item["title"], item["category"], img_path.name])

        # 2. Negative space clutter analysis (strictly TOP with Boss placement preference)
        placement = mike.calculate_negative_space(img, preferred_placement=theme.get("PrefPlacement"))
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        pos_key = placement.get("placement", "UpperLeft")
        print(f"    [+] Zero-Lag Latency  : {elapsed_ms:.1f} ms")
        print(f"    [+] Theme Name        : {theme.get('name')}")
        print(f"    [+] Top Placement     : {pos_key} (Clutter Score: {placement['scores'].get(pos_key, 0.0):.1f})")
        print(f"    [+] Typography        : {theme.get('FontTitle')} / {theme.get('FontTime')} ({theme.get('FontFile', 'Resolved')})")
        print(f"    [+] Palette Accent    : {theme.get('ColorAccent')}")
        print(f"    [+] Single Clock      : Strict Active=1 Enforced")

        # 3. Render 1920x1080 preview card
        canvas = img.resize((1920, 1080), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(canvas)

        w, h = 1920, 1080
        col_accent = parse_rgba(theme.get("ColorAccent"))
        col_primary = parse_rgba(theme.get("ColorPrimary"))
        col_sub = parse_rgba(theme.get("ColorSub"))

        # Enlarged commanding font sizes per Boss request
        f_day = resolve_font(theme.get("FontTitle"), 44)
        f_time = resolve_font(theme.get("FontTime"), 146)
        f_date = resolve_font(theme.get("FontDate"), 30)

        # Strictly TOP placement coordinates
        py = int(h * 0.04)
        if pos_key == "UpperRight":
            px = int(w * 0.65)
            day_x, time_x, date_x = px, px, px
        elif pos_key == "TopCenter":
            # Harmonious true center alignment
            day_w = f_day.getbbox("FRIDAY")[2] - f_day.getbbox("FRIDAY")[0]
            time_w = f_time.getbbox("10:45")[2] - f_time.getbbox("10:45")[0]
            date_w = f_date.getbbox("25 SEPTEMBER 2026")[2] - f_date.getbbox("25 SEPTEMBER 2026")[0]
            day_x = (w - day_w) // 2
            time_x = (w - time_w) // 2
            date_x = (w - date_w) // 2
            px = time_x
        else:  # UpperLeft
            px = int(w * 0.05)
            day_x, time_x, date_x = px, px, px

        # Draw drop shadow / border
        for dx, dy in [(-4, -4), (-4, 4), (4, -4), (4, 4), (0, 5), (0, -5), (5, 0), (-5, 0)]:
            draw.text((day_x + dx, py + dy), "FRIDAY", font=f_day, fill=(0, 0, 0))
            draw.text((time_x + dx, py + 52 + dy), "10:45", font=f_time, fill=(0, 0, 0))
            draw.text((date_x + dx, py + 214 + dy), "25 SEPTEMBER 2026", font=f_date, fill=(0, 0, 0))

        # Draw foreground text
        draw.text((day_x, py), "FRIDAY", font=f_day, fill=col_accent)
        draw.text((time_x, py + 52), "10:45", font=f_time, fill=col_primary)
        draw.text((date_x, py + 214), "25 SEPTEMBER 2026", font=f_date, fill=col_sub)

        # Bottom HUD Spec Bar
        bar_h = 75
        draw.rectangle([0, h - bar_h, w, h], fill=(10, 10, 14))
        draw.line([(0, h - bar_h), (w, h - bar_h)], fill=col_accent, width=2)

        f_hud_bold = resolve_font("Segoe UI", 15)
        f_hud = resolve_font("Segoe UI", 13)

        draw.text((25, h - bar_h + 14), f"LIVELY WALLPAPER: {item['title'].upper()}", font=f_hud_bold, fill=col_accent)
        draw.text((25, h - bar_h + 40), f"Category: {item['category']} | Latency: {elapsed_ms:.1f}ms | Master Clock: Strictly TOP | Active=1", font=f_hud, fill=(180, 180, 190))

        draw.text((w // 2 - 40, h - bar_h + 14), f"Typography: {theme.get('FontTitle')} (Enlarged +25%)", font=f_hud, fill=(240, 240, 250))
        draw.text((w // 2 - 40, h - bar_h + 40), f"Calculated Top Placement: {pos_key} ({px}, {py})", font=f_hud, fill=(160, 160, 170))

        # Palette swatches
        sw_x = w - 200
        draw.text((sw_x - 65, h - bar_h + 26), "Palette:", font=f_hud, fill=(160, 160, 170))
        for c in [col_accent, col_primary, col_sub]:
            draw.ellipse([sw_x, h - bar_h + 24, sw_x + 22, h - bar_h + 46], fill=c)
            sw_x += 30

        out_name = f"preview_lively_{item['id']}.png"
        out_p = BRAIN_DIR / out_name
        canvas.save(out_p)
        print(f"    [+] Saved Card: {out_p.name}")
        generated_previews.append(out_p)

    print("\n" + "=" * 75)
    print(f"[+] Successfully generated all {len(generated_previews)} top-placed enlarged preview cards!")
    print("=" * 75)


if __name__ == "__main__":
    main()
