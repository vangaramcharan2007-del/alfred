"""Create desktop shortcut for Naruto 4K Live Lock Screen."""
import os
import subprocess

desktop = os.path.expanduser("~/Desktop")
target = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "launch_naruto_lockscreen.bat"))
icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "wallpapers", "naruto_4k_lockscreen.jpg"))

vbs_content = f'''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{desktop}\\Naruto Live Lock Screen.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target}"
oLink.WorkingDirectory = "{os.path.dirname(target)}"
oLink.Description = "Naruto 4K Live Wallpaper Lock Screen with Clock and Date"
oLink.Save
'''

vbs_path = os.path.join(os.path.dirname(__file__), "make_shortcut.vbs")
with open(vbs_path, "w", encoding="utf-8") as f:
    f.write(vbs_content)

res = subprocess.run(["cscript", "//nologo", vbs_path], capture_output=True, text=True)
if os.path.exists(vbs_path):
    os.remove(vbs_path)

shortcut_path = os.path.join(desktop, "Naruto Live Lock Screen.lnk")
if os.path.exists(shortcut_path):
    print(f"[OK] Desktop Shortcut successfully created at: {shortcut_path}")
else:
    print("[FAIL] Shortcut was not created.")
