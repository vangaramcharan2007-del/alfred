"""
Live Demonstration of Spider (E-V) and Bat (Alfred) Symbolic Crests.
====================================================================
Tests live HTML rendering and triggers E-V and Alfred dialogue actions.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from jarvisx.gui.symbolic_crests import SPIDER_CREST_SVG, BAT_CREST_SVG
from jarvisx.automation.ev_neural_voice import speak_ev_neural


def main():
    print("=" * 80)
    print(" 🕷️ SPIDER (E-V) & 🦇 BAT (ALFRED) SYMBOLIC CREST SYSTEM")
    print("=" * 80)

    print("\n[+] 1. SPIDER CREST (E-V) EMBLEM:")
    print(f"    - Vector Path: {len(SPIDER_CREST_SVG)} chars")
    print("    - Primary Color: #00f0ff (Cyber Cyan) & #ff003c (Crimson)")
    print("    - Mode: High-Energy ADHD Pair-Programmer & Math Solver")

    print("\n[+] 2. BAT CREST (ALFRED) EMBLEM:")
    print(f"    - Vector Path: {len(BAT_CREST_SVG)} chars")
    print("    - Primary Color: #ffd700 (Dark Knight Gold) & #0a0e17 (Obsidian)")
    print("    - Mode: Sovereign Autonomous Butler & Security Gatekeeper")

    print("\n[*] Triggering E-V Neural Voice Crest Announcement...")
    speak_ev_neural("Spider and Bat crest buttons are live on your HUD, boss! Spider for E-V pair programming, and Bat for Alfred sovereign automation!")

    print("\n" + "=" * 80)
    print(" 🏆 SYMBOLIC CREST DEMONSTRATION COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
