"""
Jarvis X - Clock Theme Suite Generator
Generates customized aesthetic Rainmeter transparent clocks for all of Boss's Lively Wallpapers.
"""
import os
from pathlib import Path

SKINS_DIR = Path(r"C:\Users\vanga\OneDrive\Documents\Rainmeter\Skins")

THEMES = {
    "Ghost": {
        "folder": "GhostMinimal",
        "title": "Ghost Tactical Red",
        "font_main": "Segoe UI Light",
        "font_bold": "Segoe UI Semibold",
        "color_white": "255,255,255,245",
        "color_accent": "240,30,40,255",     # Blood Red
        "color_sub": "255,80,90,255",
        "color_muted": "220,220,220,160",
        "shadow_alpha": "240"
    },
    "Gear5": {
        "folder": "Gear5Nika",
        "title": "Sun God Nika Gear 5",
        "font_main": "Segoe UI Light",
        "font_bold": "Segoe UI Semibold",
        "color_white": "255,255,255,250",   # Pure Sun Cloud White
        "color_accent": "255,210,20,255",    # Sun God Radiance Gold
        "color_sub": "205,140,255,230",      # Conqueror Haki Violet
        "color_muted": "240,230,195,180",
        "shadow_alpha": "240"
    },
    "Tanjiro": {
        "folder": "DemonSlayerTanjiro",
        "title": "Tanjiro Hinokami Kagura",
        "font_main": "Segoe UI Light",
        "font_bold": "Segoe UI Semibold",
        "color_white": "255,255,255,245",
        "color_accent": "255,55,25,255",     # Flame Crimson
        "color_sub": "50,215,240,255",       # Nichirin Cyan
        "color_muted": "210,230,240,175",
        "shadow_alpha": "240"
    },
    "SpiderMan": {
        "folder": "SpiderManCrimson",
        "title": "Spider-Man Crimson Sky",
        "font_main": "Segoe UI Light",
        "font_bold": "Segoe UI Semibold",
        "color_white": "255,255,255,245",
        "color_accent": "255,25,50,255",     # Miles Morales Crimson
        "color_sub": "255,190,10,255",       # Venom Bio-Electricity Gold
        "color_muted": "220,210,225,170",
        "shadow_alpha": "240"
    },
    "Batman": {
        "folder": "BatmanGotham",
        "title": "Batman Gotham Rain",
        "font_main": "Segoe UI Light",
        "font_bold": "Segoe UI Semibold",
        "color_white": "235,245,255,240",   # Cold Gotham Fog
        "color_accent": "70,180,250,255",    # Neon Rain Reflection Cyan
        "color_sub": "150,175,200,220",      # Tactical Slate Blue
        "color_muted": "135,155,180,165",
        "shadow_alpha": "250"
    },
    "Naruto": {
        "folder": "NarutoSage",
        "title": "Naruto Sage Mode Chakra",
        "font_main": "Segoe UI Light",
        "font_bold": "Segoe UI Semibold",
        "color_white": "255,255,255,245",
        "color_accent": "255,130,10,255",    # Chakra Flame Orange
        "color_sub": "255,195,50,255",       # Golden Sun
        "color_muted": "245,215,165,180",
        "shadow_alpha": "240"
    },
    "Arthur": {
        "folder": "ArthurMorganRDR",
        "title": "Arthur Morgan Outlaw Sunset",
        "font_main": "Segoe UI Light",
        "font_bold": "Segoe UI Semibold",
        "color_white": "255,248,235,245",   # Warm Parchment
        "color_accent": "255,145,25,255",    # Sunset Amber
        "color_sub": "220,170,95,255",       # Outlaw Gold
        "color_muted": "215,190,155,170",
        "shadow_alpha": "240"
    },
    "Matrix": {
        "folder": "MatrixRain",
        "title": "Matrix Cyberpunk Green",
        "font_main": "Consolas",
        "font_bold": "Consolas",
        "color_white": "215,255,225,245",   # Digital White-Green
        "color_accent": "0,255,110,255",     # Terminal Phosphor Green
        "color_sub": "55,255,165,255",       # High Voltage Matrix Green
        "color_muted": "110,205,140,175",
        "shadow_alpha": "250"
    }
}

TEMPLATE = """[Rainmeter]
Update=1000
AccurateText=1
DynamicWindowSize=1

[Metadata]
Name={title}
Author=Jarvis X
Information=Ultra-sleek aesthetic minimalist typography clock customized for Boss.
Version=1.0.0

[Variables]
FontName={font_main}
FontBold={font_bold}
ColorWhite={color_white}
ColorAccent={color_accent}
ColorSub={color_sub}
ColorMuted={color_muted}

; ==============================
; MEASURES
; ==============================

[MeasureHour]
Measure=Time
Format=%I

[MeasureMinute]
Measure=Time
Format=%M

[MeasureAmPm]
Measure=Time
Format=%p

[MeasureDay]
Measure=Time
Format=%A

[MeasureDate]
Measure=Time
Format=%d %B %Y

; ==============================
; METERS
; ==============================

; Day of week in theme accent color
[MeterDay]
Meter=String
MeasureName=MeasureDay
X=4
Y=0
FontColor=#ColorAccent#
FontFace=#FontBold#
FontSize=16
StringCase=Upper
StringEffect=Shadow
FontEffectColor=0,0,0,{shadow_alpha}
AntiAlias=1
InlineSetting=CharacterSpacing | 5 | 5

; Main Hour
[MeterHour]
Meter=String
MeasureName=MeasureHour
X=0
Y=24
FontColor=#ColorWhite#
FontFace=#FontName#
FontSize=88
StringEffect=Shadow
FontEffectColor=0,0,0,{shadow_alpha}
AntiAlias=1

; Glowing Colon in Theme Accent Color
[MeterColon]
Meter=String
X=([MeterHour:X] + [MeterHour:W] - 6)
Y=28
FontColor=#ColorAccent#
FontFace=#FontBold#
FontSize=78
Text=":"
StringEffect=Shadow
FontEffectColor=0,0,0,{shadow_alpha}
AntiAlias=1
DynamicVariables=1

; Minute
[MeterMinute]
Meter=String
MeasureName=MeasureMinute
X=([MeterColon:X] + [MeterColon:W] - 4)
Y=24
FontColor=#ColorWhite#
FontFace=#FontName#
FontSize=88
StringEffect=Shadow
FontEffectColor=0,0,0,{shadow_alpha}
AntiAlias=1
DynamicVariables=1

; AM / PM indicator
[MeterAmPm]
Meter=String
MeasureName=MeasureAmPm
X=([MeterMinute:X] + [MeterMinute:W] + 8)
Y=42
FontColor=#ColorSub#
FontFace=#FontBold#
FontSize=16
StringCase=Upper
StringEffect=Shadow
FontEffectColor=0,0,0,{shadow_alpha}
AntiAlias=1
DynamicVariables=1

; Full Date: e.g. 22 SEPTEMBER 2026
[MeterDate]
Meter=String
MeasureName=MeasureDate
X=4
Y=([MeterHour:Y] + [MeterHour:H] - 10)
FontColor=#ColorMuted#
FontFace=#FontBold#
FontSize=13
StringCase=Upper
StringEffect=Shadow
FontEffectColor=0,0,0,{shadow_alpha}
AntiAlias=1
DynamicVariables=1
InlineSetting=CharacterSpacing | 3 | 3
"""

def generate_all():
    print(f"[*] Generating {len(THEMES)} custom Rainmeter clock skins...")
    for key, cfg in THEMES.items():
        folder_path = SKINS_DIR / cfg["folder"] / "Clock"
        folder_path.mkdir(parents=True, exist_ok=True)
        ini_file = folder_path / "clock.ini"
        
        content = TEMPLATE.format(**cfg)
        with open(ini_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [+] Created: {cfg['folder']} -> {cfg['title']}")

    print("[SUCCESS] All 8 custom aesthetic clock skins created in Rainmeter directory!")

if __name__ == "__main__":
    generate_all()
