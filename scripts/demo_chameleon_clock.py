#!/usr/bin/env python3
"""
Jarvis X - Chameleon Clock Live Demonstration Script
Demonstrates end-to-end adaptive aesthetic clock:
1. Tests wallpaper analysis on multiple themes (Naruto Chakra vs Kyoto Twilight).
2. Proves dynamic color palette extraction & negative-space placement.
3. Updates the live desktop widget on Boss's screen.
"""

import os
import sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.wallpaper_chameleon_engine import run_chameleon

WALLPAPERS = [
    os.path.join(PROJECT_ROOT, "assets", "wallpapers", "naruto_4k_lockscreen.jpg"),
    os.path.join(PROJECT_ROOT, "assets", "wallpapers", "kyoto_pagoda_twilight.jpg"),
]

def demonstrate():
    print("=" * 65)
    print("      JARVIS X - ADAPTIVE CHAMELEON CLOCK DEMONSTRATION")
    print("=" * 65)

    for i, wp in enumerate(WALLPAPERS):
        print(f"\n[PHASE {i+1}] Applying Theme & Analyzing: {os.path.basename(wp)}")
        if not os.path.exists(wp):
            print(f"[-] File not found: {wp}")
            continue

        # Set wallpaper using PowerShell P/Invoke script
        ps_script = os.path.join(CURRENT_DIR, "set_wallpaper.ps1")
        cmd = f'powershell -ExecutionPolicy Bypass -File "{ps_script}" -ImagePath "{wp}"'
        print(f"[*] Switching desktop wallpaper...")
        os.system(cmd)
        time.sleep(1)

        # Run Chameleon engine
        print(f"[*] Running Chameleon Engine...")
        success = run_chameleon(wallpaper_path=wp, pref="smart")
        print(f"[+] Phase {i+1} Result: {'SUCCESS' if success else 'FAILED'}")
        time.sleep(2)

    # Return to Naruto as primary aesthetic theme
    print("\n[FINAL] Restoring Boss's Primary Theme (Naruto Sage 4K)...")
    primary_wp = WALLPAPERS[0]
    ps_script = os.path.join(CURRENT_DIR, "set_wallpaper.ps1")
    os.system(f'powershell -ExecutionPolicy Bypass -File "{ps_script}" -ImagePath "{primary_wp}"')
    run_chameleon(wallpaper_path=primary_wp, pref="smart_center", on_top=0)
    print("[+] Chameleon Clock is now active, centered, and color-matched to Naruto Sage mode!")
    print("=" * 65)

if __name__ == "__main__":
    demonstrate()
