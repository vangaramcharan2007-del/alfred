#!/usr/bin/env python3
"""
Jarvis X - Aesthetic Centered Battlestation Clock Deployer
Deploys a centered aesthetic anime/cyberpunk clock to Rainmeter with live hardware telemetry,
Kanji/English typography, dynamic palette cycling, and sets Rainmeter.ini coordinates to dead center.
"""

import os
import sys
import subprocess
import shutil

SKINS_DIR = r"C:\Users\vanga\OneDrive\Documents\Rainmeter\Skins"
RAINMETER_INI = os.path.expanduser(r"~\AppData\Roaming\Rainmeter\Rainmeter.ini")
RAINMETER_EXE = r"C:\Program Files\Rainmeter\Rainmeter.exe"

SKIN_NAME = "JarvisAestheticClock"
SKIN_FOLDER = os.path.join(SKINS_DIR, SKIN_NAME)
INI_FILE = os.path.join(SKIN_FOLDER, "Clock.ini")

SKIN_CONTENT = """[Rainmeter]
Update=1000
AccurateText=1
DynamicWindowSize=1
BackgroundMode=2
SolidColor=0,0,0,1
LeftMouseDoubleClickAction=[!SetVariable PaletteMode ((#PaletteMode# % 5) + 1)][!WriteKeyValue Variables PaletteMode "((#PaletteMode# % 5) + 1)"][!Refresh]

[Metadata]
Name=Jarvis Centered Aesthetic Clock
Author=Jarvis X / Alfred
Information=Ultra-sleek aesthetic centered anime & cyberpunk battlestation clock for Boss.
Version=2.0.0

[Variables]
PaletteMode=1
Scale=1.0

; === PALETTE PRESETS ===
; 1: Tokyo Night Neon (Default)
; 2: Naruto Sage Chakra
; 3: Sun God Nika
; 4: Cyber Crimson (Demon Slayer)
; 5: Batman Gotham Electric

ColorPrimary=255,255,255,250

; Dynamic Color Assignment
ColorAccent=(#PaletteMode# = 1 ? 56,189,248,255 : (#PaletteMode# = 2 ? 255,130,10,255 : (#PaletteMode# = 3 ? 251,191,36,255 : (#PaletteMode# = 4 ? 239,68,68,255 : 59,130,246,255))))
ColorSecondary=(#PaletteMode# = 1 ? 192,132,252,240 : (#PaletteMode# = 2 ? 250,204,21,240 : (#PaletteMode# = 3 ? 255,255,255,240 : (#PaletteMode# = 4 ? 6,182,212,240 : 148,163,184,240))))
ColorMuted=203,213,225,180
ColorBadgeBg=15,23,42,160

; Fonts
FontLight=Segoe UI Light
FontSemibold=Segoe UI Semibold
FontBold=Segoe UI
FontMono=Consolas

; ==============================
; MEASURES
; ==============================

[MeasureTime]
Measure=Time
Format=%I:%M

[MeasureHour]
Measure=Time
Format=%I

[MeasureMinute]
Measure=Time
Format=%M

[MeasureAmPm]
Measure=Time
Format=%p

[MeasureDayEnglish]
Measure=Time
Format=%A

[MeasureDayKanji]
Measure=Time
Format=%w
Substitute="0":"日 曜 日","1":"月 曜 日","2":"火 曜 日","3":"水 曜 日","4":"木 曜 日","5":"金 曜 日","6":"土 曜 日"

[MeasureDate]
Measure=Time
Format=%d  %B  %Y

[MeasureCPU]
Measure=CPU
UpdateDivider=2

[MeasureRAM]
Measure=PhysicalMemory
UpdateDivider=4

; ==============================
; METERS (ALL CENTER-ALIGNED)
; ==============================

; 1. Top Kanji & English Day Header with Accent Dots
[MeterHeader]
Meter=String
MeasureName=MeasureDayEnglish
MeasureName2=MeasureDayKanji
StringAlign=Center
FontFace=#FontSemibold#
FontSize=(13 * #Scale#)
FontColor=#ColorAccent#
X=(320 * #Scale#)
Y=0
Text="[ %2  •  %1 ]"
StringCase=Upper
StringEffect=Shadow
FontEffectColor=0,0,0,220
AntiAlias=1
InlineSetting=CharacterSpacing | (3 * #Scale#) | (3 * #Scale#)
DynamicVariables=1

; 2. Giant Aesthetic Time Display (92pt)
[MeterTime]
Meter=String
MeasureName=MeasureTime
StringAlign=Center
FontFace=#FontLight#
FontSize=(90 * #Scale#)
FontColor=#ColorPrimary#
X=(300 * #Scale#)
Y=(20 * #Scale#)
StringEffect=Shadow
FontEffectColor=0,0,0,230
AntiAlias=1
DynamicVariables=1

; 3. Small Modern AM/PM Badge
[MeterAmPm]
Meter=String
MeasureName=MeasureAmPm
StringAlign=Left
FontFace=#FontSemibold#
FontSize=(14 * #Scale#)
FontColor=#ColorSecondary#
X=(510 * #Scale#)
Y=(50 * #Scale#)
StringCase=Upper
StringEffect=Shadow
FontEffectColor=0,0,0,220
AntiAlias=1
DynamicVariables=1

; 4. Full Elegant Date
[MeterDate]
Meter=String
MeasureName=MeasureDate
StringAlign=Center
FontFace=#FontSemibold#
FontSize=(14 * #Scale#)
FontColor=#ColorMuted#
X=(320 * #Scale#)
Y=(162 * #Scale#)
StringCase=Upper
StringEffect=Shadow
FontEffectColor=0,0,0,220
AntiAlias=1
InlineSetting=CharacterSpacing | (4 * #Scale#) | (4 * #Scale#)
DynamicVariables=1

; 5. Sleek Live Telemetry Pill / Jarvis Status
[MeterPillBg]
Meter=Shape
Shape=Rectangle 0,0,(380 * #Scale#),(26 * #Scale#),13 | Fill Color #ColorBadgeBg# | StrokeWidth 1 | Stroke Color #ColorAccent#
X=(130 * #Scale#)
Y=(194 * #Scale#)
DynamicVariables=1

[MeterTelemetry]
Meter=String
MeasureName=MeasureCPU
MeasureName2=MeasureRAM
StringAlign=Center
FontFace=#FontMono#
FontSize=(10 * #Scale#)
FontColor=#ColorSecondary#
X=(320 * #Scale#)
Y=(198 * #Scale#)
Text="❖ JARVIS X  •  CPU %1%  •  RAM %2%  •  ONLINE"
StringEffect=Shadow
FontEffectColor=0,0,0,200
AntiAlias=1
DynamicVariables=1
"""

def update_rainmeter_ini():
    """Configure Rainmeter.ini so JarvisAestheticClock is active and centered, and old clocks deactivated."""
    if not os.path.exists(RAINMETER_INI):
        print(f"[!] Rainmeter.ini not found at {RAINMETER_INI}")
        return False

    with open(RAINMETER_INI, "r", encoding="utf-16", errors="ignore") as f:
        content = f.read()

    # Deactivate old top-left minimal clock
    content = content.replace("[GhostMinimal\\Clock]\nActive=1", "[GhostMinimal\\Clock]\nActive=0")
    content = content.replace("[GhostMinimal\\Clock]\r\nActive=1", "[GhostMinimal\\Clock]\r\nActive=0")

    # Add or update JarvisAestheticClock section
    section_name = f"[{SKIN_NAME}]"
    section_body = (
        f"{section_name}\n"
        "Active=1\n"
        "WindowX=50%\n"
        "WindowY=28%\n"
        "AnchorX=50%\n"
        "AnchorY=50%\n"
        "ClickThrough=0\n"
        "Draggable=1\n"
        "SnapToScreen=0\n"
        "KeepOnScreen=1\n"
        "AlwaysOnTop=-2\n"
    )

    if section_name in content:
        # Replace existing section
        import re
        content = re.sub(rf"\[{SKIN_NAME}\][^\[]*", section_body, content)
    else:
        content += f"\n{section_body}\n"

    with open(RAINMETER_INI, "w", encoding="utf-16") as f:
        f.write(content)

    print("[+] Rainmeter.ini updated: JarvisAestheticClock positioned at WindowX=50%, WindowY=28% (Dead Center).")
    return True

def deploy():
    print(f"[*] Deploying {SKIN_NAME}...")
    os.makedirs(SKIN_FOLDER, exist_ok=True)

    # Save Clock.ini in UTF-16
    with open(INI_FILE, "w", encoding="utf-16") as f:
        f.write(SKIN_CONTENT)
    print(f"[+] Written Clock.ini to {INI_FILE}")

    # Copy to workspace backup
    ws_backup = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "skins", SKIN_NAME)
    os.makedirs(ws_backup, exist_ok=True)
    with open(os.path.join(ws_backup, "Clock.ini"), "w", encoding="utf-8") as f:
        f.write(SKIN_CONTENT)
    print(f"[+] Mirrored backup to workspace: assets/skins/{SKIN_NAME}/Clock.ini")

    # Update Rainmeter.ini coordinates
    update_rainmeter_ini()

    # Tell Rainmeter to refresh and activate
    try:
        subprocess.run([RAINMETER_EXE, "!RefreshApp"], check=False)
        subprocess.run([RAINMETER_EXE, "!ActivateConfig", SKIN_NAME, "Clock.ini"], check=False)
        print("[+] Sent !RefreshApp and !ActivateConfig to Rainmeter process.")
    except Exception as e:
        print(f"[!] Warning communicating with Rainmeter.exe: {e}")

if __name__ == "__main__":
    deploy()
