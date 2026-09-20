"""
Standalone Windows Screensaver Entrypoint for Naruto 4K Live Lock Screen.
Zero heavy dependencies - compiles in seconds.
"""

import sys
import os
import subprocess
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(BASE_DIR, "src", "jarvisx", "gui", "naruto_lockscreen.html")

BROWSER_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_browser():
    for p in BROWSER_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def main():
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "/s"

    if "/c" in arg:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            "Naruto 4K Live Wallpaper Lock Screen\n\nPlaying: E:\\naruto-endless-sky.3840x2160.mp4\nReal-time digital clock, date, and Shinobi HUD.\n\nPress any key or swipe up to unlock.",
            "Naruto 4K Lock Screen Settings",
            0x40
        )
        sys.exit(0)
    elif "/p" in arg:
        # Mini preview in control panel
        sys.exit(0)

    # Launch live lockscreen
    browser = find_browser()
    if not browser:
        sys.exit(1)

    profile = os.path.join(tempfile.gettempdir(), "naruto_lock_runtime_profile")
    file_url = "file:///" + HTML_PATH.replace("\\", "/")

    cmd = [
        browser,
        f"--app={file_url}",
        f"--user-data-dir={profile}",
        "--kiosk",
        "--start-fullscreen",
        "--disable-pinch",
        "--overscroll-history-navigation=0",
        "--no-first-run"
    ]
    if "msedge" in browser.lower():
        cmd.append("--edge-kiosk-type=fullscreen")

    proc = subprocess.Popen(cmd)
    proc.wait()


if __name__ == "__main__":
    main()
