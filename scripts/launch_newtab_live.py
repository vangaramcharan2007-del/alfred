import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWTAB_PATH = os.path.join(PROJECT_ROOT, "newtab", "index.html")

def find_browser():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def launch():
    browser = find_browser()
    file_url = f"file:///{NEWTAB_PATH.replace(os.sep, '/')}"
    print(f"[LAUNCH] Launching browser: {browser}")
    print(f"[LAUNCH] URL: {file_url}")
    if browser:
        cmd = [
            browser,
            "--start-maximized",
            "--autoplay-policy=no-user-gesture-required",
            "--allow-file-access-from-files",
            file_url
        ]
        proc = subprocess.Popen(cmd)
        print("[OK] Opened live on user's display.")
        return proc
    else:
        # Fallback to default system browser
        os.startfile(file_url)
        print("[OK] Opened via default shell.")
        return None

if __name__ == "__main__":
    launch()
