import os
import sys
import subprocess
from pathlib import Path

script_path = Path(__file__).resolve().parent / "auto_clock_sync.pyw"
project_dir = script_path.parent.parent

# Launch pythonw process in background
proc = subprocess.Popen(["pythonw", str(script_path)], cwd=str(project_dir))
print(f"[SUCCESS] Auto-sync daemon launched silently with PID: {proc.pid}")

# Add to Windows Startup
try:
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    startup_dir = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    shortcut_path = startup_dir / "JarvisClockSync.lnk"
    
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = "pythonw.exe"
    shortcut.Arguments = f'"{script_path}"'
    shortcut.WorkingDirectory = str(project_dir)
    shortcut.WindowStyle = 7  # Minimized / silent
    shortcut.save()
    print(f"[SUCCESS] Startup shortcut created: {shortcut_path}")
except Exception as e:
    # Fallback to .bat in startup
    startup_dir = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    bat_path = startup_dir / "jarvis_clock_sync.bat"
    with open(bat_path, "w") as f:
        f.write(f'@start "" pythonw "{script_path}"\n')
    print(f"[SUCCESS] Startup batch file created: {bat_path}")
