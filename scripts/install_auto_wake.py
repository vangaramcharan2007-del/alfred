"""Install AutoWakeSentinel into Windows Startup folder."""
import os
import subprocess

startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vbs_target = os.path.join(project_dir, "scripts", "start_auto_wake_sentinel.vbs")

vbs_code = f'''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{startup_dir}\\NarutoAutoWakeSentinel.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "wscript.exe"
oLink.Arguments = """{vbs_target}"""
oLink.WorkingDirectory = "{project_dir}"
oLink.Description = "Naruto 4K Live Lock Screen Auto-Wake Sentinel"
oLink.Save
'''

temp_vbs = os.path.join(project_dir, "scripts", "temp_startup.vbs")
with open(temp_vbs, "w", encoding="utf-8") as f:
    f.write(vbs_code)

res = subprocess.run(["cscript", "//nologo", temp_vbs], capture_output=True, text=True)
if os.path.exists(temp_vbs):
    os.remove(temp_vbs)

lnk_path = os.path.join(startup_dir, "NarutoAutoWakeSentinel.lnk")
if os.path.exists(lnk_path):
    print(f"[OK] Successfully installed Auto-Wake Sentinel into Startup: {lnk_path}")
else:
    print(f"[FAIL] Could not install into Startup.")
