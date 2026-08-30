"""
Jarvis X — Chrome Extension Setup & Web Store Dispatcher.
Launches the local Alfred Extension Bridge server and opens Chrome to install proposed extensions.
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add src/ to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from jarvisx.runtime.extension_server import start_extension_server

PROPOSED_EXTENSIONS = [
    {
        "name": "LeetHub v3 (Auto-sync LeetCode to GitHub)",
        "url": "https://chromewebstore.google.com/detail/leethub-v3/kdnlfbcakpmdnpomfdkfjodpkimdbbdf"
    },
    {
        "name": "Refined LeetCode (Clean UI & Complexity Estimator)",
        "url": "https://chromewebstore.google.com/detail/refined-leetcode/eamjnbcbfmoackfblalhaeckkefelidg"
    },
    {
        "name": "Octotree (GitHub Code Tree IDE Explorer)",
        "url": "https://chromewebstore.google.com/detail/octotree-github-code-tr/bkhaagjahfmjlj hempcgldjadogjdijk"
    },
    {
        "name": "JSON Viewer Pro (Syntax Highlighting & Formatter)",
        "url": "https://chromewebstore.google.com/detail/json-viewer-pro/eifflpmocdbdmepbjaipkndgjednakjd"
    },
    {
        "name": "daily.dev (Curated Developer News & DSA Roadmap)",
        "url": "https://chromewebstore.google.com/detail/dailydev-the-homepage-eve/jlmpdalbgfljbghbfekgnheemkfcmbed"
    }
]

def main():
    print("\n" + "=" * 75)
    print("   JARVIS X — CHROME EXTENSION DEPLOYER & COMPANION BRIDGE")
    print("=" * 75 + "\n")

    # 1. Start Local Bridge Server
    print("[+] 1. Initializing Local Alfred Extension Bridge on port 8765...")
    server = start_extension_server()
    if server.running:
        print("    🟢 Extension Bridge Online: http://127.0.0.1:8765")
    else:
        print("    ⚠️ Could not bind port 8765 (may already be in use)")

    extension_folder = Path(__file__).parent.parent / "extensions" / "alfred-chrome-companion"
    abs_folder = extension_folder.resolve()
    print(f"\n[+] 2. Alfred Companion Extension is ready at:")
    print(f"    📁 {abs_folder}\n")

    # 2. Open Installation Instructions & Links
    print("[+] 3. Dispatching Chrome Web Store pages for proposed developer extensions:")
    for ext in PROPOSED_EXTENSIONS:
        print(f"    • Opening: {ext['name']}...")
        webbrowser.open(ext["url"])
        time.sleep(0.4)

    # 3. Open Chrome Extensions Page
    print("\n[+] 4. Opening 'chrome://extensions'...")
    try:
        subprocess.Popen(["start", "chrome", "chrome://extensions"], shell=True)
    except Exception:
        webbrowser.open("chrome://extensions")

    print("\n" + "=" * 75)
    print("   HOW TO LOAD ALFRED COMPANION IN CHROME (2 Simple Steps):")
    print("=" * 75)
    print("   1. In Chrome, go to: chrome://extensions")
    print("   2. Toggle 'Developer mode' in the top-right corner to ON.")
    print("   3. Click 'Load unpacked' in the top-left corner.")
    print(f"   4. Select the folder: {abs_folder}")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    main()
