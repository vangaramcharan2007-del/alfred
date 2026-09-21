"""
Jarvis X - Instant Clock Theme Switcher
Instantly switches the active Rainmeter transparent clock to match Boss's chosen Lively wallpaper.
"""
import sys
import subprocess
import time
from pathlib import Path

RAINMETER_EXE = Path(r"C:\Program Files\Rainmeter\Rainmeter.exe")

THEMES = {
    "ghost": ("GhostMinimal\\Clock", "clock.ini", "Ghost Tactical Red (Blood Red & White)"),
    "gear5": ("Gear5Nika\\Clock", "clock.ini", "Sun God Nika Gear 5 (Cloud White & Radiant Gold)"),
    "tanjiro": ("DemonSlayerTanjiro\\Clock", "clock.ini", "Tanjiro Hinokami Kagura (Flame Crimson & Nichirin Cyan)"),
    "spiderman": ("SpiderManCrimson\\Clock", "clock.ini", "Spider-Man Crimson Sky (Miles Morales Crimson & Gold)"),
    "batman": ("BatmanGotham\\Clock", "clock.ini", "Batman Gotham Rain (Rain Cyan & Industrial Slate)"),
    "naruto": ("NarutoSage\\Clock", "clock.ini", "Naruto Sage Mode (Chakra Flame Orange & Sun Gold)"),
    "arthur": ("ArthurMorganRDR\\Clock", "clock.ini", "Arthur Morgan Outlaw Sunset (Western Amber & Sepia Gold)"),
    "matrix": ("MatrixRain\\Clock", "clock.ini", "Matrix Cyberpunk Green (Terminal Code Phosphor Green)")
}

def switch_clock(theme_name: str, x="50%", y="110"):
    key = theme_name.lower().replace(" ", "").replace("-", "").replace("_", "")
    
    # Fuzzy match
    matched = None
    for k in THEMES:
        if k in key or key in k:
            matched = k
            break
            
    if not matched:
        print(f"[-] Unknown theme: '{theme_name}'")
        print("Available themes:")
        for k, (_, _, desc) in THEMES.items():
            print(f"  - {k:<10} : {desc}")
        return False

    config_name, ini_file, desc = THEMES[matched]
    print(f"[*] Activating Clock Theme: {desc}...")

    # Deactivate all known themes first to ensure no overlap
    for k, (cfg, _, _) in THEMES.items():
        subprocess.run([str(RAINMETER_EXE), "!DeactivateConfig", cfg], capture_output=True)
    subprocess.run([str(RAINMETER_EXE), "!DeactivateConfig", "Mond\\Clock"], capture_output=True)
    
    time.sleep(0.2)

    # Activate selected
    subprocess.run([str(RAINMETER_EXE), "!ActivateConfig", config_name, ini_file], capture_output=True)
    time.sleep(0.2)

    # Position at top center
    subprocess.run([str(RAINMETER_EXE), "!Move", x, y, config_name], capture_output=True)
    subprocess.run([str(RAINMETER_EXE), "!RefreshApp"], capture_output=True)

    print(f"[SUCCESS] {desc} is now LIVE on your desktop!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("=== Jarvis X Clock Theme Switcher ===")
        print("Usage: python switch_clock_theme.py <theme>")
        print("\nAvailable Themes:")
        for k, (_, _, desc) in THEMES.items():
            print(f"  {k:<12} -> {desc}")
    else:
        theme_arg = sys.argv[1]
        y_pos = sys.argv[2] if len(sys.argv) > 2 else "110"
        switch_clock(theme_arg, y=y_pos)
