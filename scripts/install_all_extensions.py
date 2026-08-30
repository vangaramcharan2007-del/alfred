"""
Jarvis X — Mass Extension Installer & Web Store Dispatcher.
Opens all top-tier Chrome extensions in Google Chrome for immediate 1-click installation.
"""

import os
import sys
import time
import webbrowser
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ALL_EXTENSIONS = [
    # Developer & DSA
    ("LeetHub v3", "https://chromewebstore.google.com/detail/leethub-v3/kdnlfbcakpmdnpomfdkfjodpkimdbbdf"),
    ("Refined LeetCode", "https://chromewebstore.google.com/detail/refined-leetcode/eamjnbcbfmoackfblalhaeckkefelidg"),
    ("Octotree", "https://chromewebstore.google.com/detail/octotree-github-code-tr/bkhaagjahfmjljhempcgldjadogjdijk"),
    ("JSON Viewer Pro", "https://chromewebstore.google.com/detail/json-viewer-pro/eifflpmocdbdmepbjaipkndgjednakjd"),
    ("daily.dev", "https://chromewebstore.google.com/detail/dailydev-the-homepage-eve/jlmpdalbgfljbghbfekgnheemkfcmbed"),
    ("Wappalyzer", "https://chromewebstore.google.com/detail/wappalyzer-technology-pro/gppongmhjkpfnbhagpmjfkannfbllamg"),
    ("Tampermonkey", "https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo"),

    # Productivity & Workflow
    ("Toby for Tabs", "https://chromewebstore.google.com/detail/toby-for-tabs/hddnkoipeegfoeaoibdmnaalmgkpipda"),
    ("Raindrop.io", "https://chromewebstore.google.com/detail/raindropio/ldgfbffkinooeloadekpmfoklnobpien"),

    # Privacy & Utilities
    ("uBlock Origin", "https://chromewebstore.google.com/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm"),
    ("Dark Reader", "https://chromewebstore.google.com/detail/dark-reader/eimadpbcbfnmbkopoojfekhnkhdbieeh"),
    ("Bitwarden", "https://chromewebstore.google.com/detail/bitwarden-free-password-m/nngceckbapebfimnlniiiahkandclblb"),
    ("SponsorBlock for YouTube", "https://chromewebstore.google.com/detail/sponsorblock-for-youtube/mnjggcdmjocbbbhaepdhchncahnbgone"),
    ("Volume Master", "https://chromewebstore.google.com/detail/volume-master/jghecgabfgfdldnmbfkhmffcabddioke"),
]

def main():
    print("\n" + "=" * 75)
    print("   ALFRED OS — MASS CHROME EXTENSION INSTALLER DISPATCH")
    print("=" * 75 + "\n")

    print(f"[+] Dispatching {len(ALL_EXTENSIONS)} essential Chrome extensions to your browser:")
    for name, url in ALL_EXTENSIONS:
        print(f"  • Opening [{name}]...")
        try:
            # Use windows start command with chrome if possible for clean tab grouping
            subprocess.Popen(["start", "chrome", url], shell=True)
        except Exception:
            webbrowser.open(url)
        time.sleep(0.4)

    print("\n[+] All extension pages have been opened in Chrome!")
    print("    👉 Click 'Add to Chrome' on each opened tab to install.")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    main()
