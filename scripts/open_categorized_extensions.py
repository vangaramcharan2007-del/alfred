"""
Jarvis X — Comprehensive Chrome Extension Suite Dispatcher across All Chrome Web Store Categories.
"""

import os
import sys
import webbrowser
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CATEGORY_EXTENSIONS = {
    "Productivity & Workflow": [
        {"name": "Toby for Tabs", "desc": "Visual workspace tab manager", "url": "https://chromewebstore.google.com/detail/toby-for-tabs/hddnkoipeegfoeaoibdmnaalmgkpipda"},
        {"name": "Raindrop.io", "desc": "All-in-one bookmark manager & web clipper", "url": "https://chromewebstore.google.com/detail/raindropio/ldgfbffkinooeloadekpmfoklnobpien"},
        {"name": "Notion Web Clipper", "desc": "Save any page directly into Notion databases", "url": "https://chromewebstore.google.com/detail/notion-web-clipper/knheggckgoiihginacbkhaalnibhilkk"},
        {"name": "Clockify Time Tracker", "desc": "Track productivity and study sessions", "url": "https://chromewebstore.google.com/detail/clockify-time-tracker/pmjeegjhjdlccodhacdnmmpem объек"},
    ],
    "Developer Tools & Web Inspection": [
        {"name": "Wappalyzer", "desc": "Identify technology stacks on any website", "url": "https://chromewebstore.google.com/detail/wappalyzer-technology-pro/gppongmhjkpfnbhagpmjfkannfbllamg"},
        {"name": "Tampermonkey", "desc": "Execute user scripts and automated DOM extensions", "url": "https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo"},
        {"name": "Web Developer", "desc": "Official suite of web analysis & layout tools", "url": "https://chromewebstore.google.com/detail/web-developer/bfbameneiokkgbdmiekhjnmfkcnldhhm"},
        {"name": "React Developer Tools", "desc": "Inspect React component hierarchies", "url": "https://chromewebstore.google.com/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi"},
    ],
    "Education & AI Learning": [
        {"name": "Wolfram|Alpha", "desc": "Instant computational intelligence and mathematics", "url": "https://chromewebstore.google.com/detail/wolframalpha/icncamkooinmbehmilhcelhkkgoppabm"},
        {"name": "Language Reactor", "desc": "Dual subtitles & translation for YouTube learning", "url": "https://chromewebstore.google.com/detail/language-reactor/hoombieeljmmljlkjmnhekg наде"},
        {"name": "SponsorBlock for YouTube", "desc": "Auto-skip sponsored segments in tech tutorials", "url": "https://chromewebstore.google.com/detail/sponsorblock-for-youtube/mnjggcdmjocbbbhaepdhchncahnbgone"},
    ],
    "Privacy & Security": [
        {"name": "uBlock Origin", "desc": "The most efficient wide-spectrum content blocker", "url": "https://chromewebstore.google.com/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm"},
        {"name": "Bitwarden Password Manager", "desc": "Open-source zero-knowledge password vault", "url": "https://chromewebstore.google.com/detail/bitwarden-free-password-m/nngceckbapebfimnlniiiahkandclblb"},
        {"name": "Privacy Badger", "desc": "EFF automated invisible tracker blocker", "url": "https://chromewebstore.google.com/detail/privacy-badger/pkehgijcmpdhfbdbbkihnmdoongendcb"},
    ],
    "Functionality, UI & Lifestyle": [
        {"name": "Dark Reader", "desc": "High-contrast dark mode for every website", "url": "https://chromewebstore.google.com/detail/dark-reader/eimadpbcbfnmbkopoojfekhnkhdbieeh"},
        {"name": "Vimium", "desc": "Keyboard-only navigation for the entire web", "url": "https://chromewebstore.google.com/detail/vimium/dbepggeogbaibhgnhhndojpepiihcmeb"},
        {"name": "Volume Master", "desc": "Up to 600% volume boost for quiet audio/videos", "url": "https://chromewebstore.google.com/detail/volume-master/jghecgabfgfdldnmbfkhmffcabddioke"},
    ],
    "Well-Being & Health": [
        {"name": "Water Reminder (Hydro)", "desc": "Hydration tracking reminders during work", "url": "https://chromewebstore.google.com/detail/water-reminder/kikbppgnednfnkbfckhkchhhidgnljep"},
        {"name": "Screen Shader | 20-20-20 Eye Care", "desc": "Blue light reduction and eye strain prevention", "url": "https://chromewebstore.google.com/detail/screen-shader-smart-scree/fmlmepmnncojeeggpmddnegncgahmc jl"},
    ]
}

def open_category(category_name: str):
    """Open all extensions in a specific category."""
    exts = CATEGORY_EXTENSIONS.get(category_name)
    if not exts:
        print(f"Unknown category: {category_name}")
        return
    print(f"\n[+] Opening {len(exts)} extensions for '{category_name}' in Chrome:")
    for ext in exts:
        print(f"  • {ext['name']} -> {ext['desc']}")
        webbrowser.open(ext["url"])
        time.sleep(0.3)

def open_all():
    """Open the top extension from each category."""
    print("\n[+] Opening top extension from each category:")
    for cat, exts in CATEGORY_EXTENSIONS.items():
        top = exts[0]
        print(f"  • [{cat}] {top['name']}")
        webbrowser.open(top["url"])
        time.sleep(0.3)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cat_arg = " ".join(sys.argv[1:])
        open_category(cat_arg)
    else:
        print("Usage: python scripts/open_categorized_extensions.py [Category Name]")
        print("Available Categories:")
        for c in CATEGORY_EXTENSIONS:
            print(f"  - {c}")
