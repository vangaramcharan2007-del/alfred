"""Launch Naruto 4K Live Lock Screen immediately on the active Windows desktop."""
import os
import subprocess

edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
html_path = r"c:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\src\jarvisx\gui\naruto_lockscreen.html"
file_url = "file:///" + html_path.replace("\\", "/")
profile = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\Temp"), "Temp", "naruto_lock_runtime_profile")

cmd = [
    edge,
    f"--app={file_url}",
    f"--user-data-dir={profile}",
    "--kiosk",
    "--edge-kiosk-type=fullscreen",
    "--start-fullscreen",
    "--disable-pinch",
    "--overscroll-history-navigation=0",
    "--no-first-run"
]

subprocess.Popen(cmd)
print("[OK] Naruto 4K Live Lock Screen is now active on your display.")
