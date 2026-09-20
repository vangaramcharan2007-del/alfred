"""
Windows Startup & Desktop Integration for Jarvis X / E.V.
=========================================================
Configures the master launcher for Jarvis X Omnipresent Living Core.
Provides a portable launcher script that boots the HUD, Eevee voice,
ambient watcher, and tray icon.
"""

import os
import sys
from pathlib import Path

# UTF-8 safe stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BAT_PATH = PROJECT_ROOT / "run_jarvis_omnipresent.bat"


def get_pythonw_path() -> str:
    """Finds pythonw.exe for windowless execution."""
    python_exe = Path(sys.executable)
    pythonw_exe = python_exe.parent / "pythonw.exe"
    if pythonw_exe.exists():
        return str(pythonw_exe)
    return str(python_exe)


def generate_desktop_launcher():
    """Creates a desktop launcher script in the project directory."""
    pythonw = get_pythonw_path()
    vbs_path = PROJECT_ROOT / "launch_silent_jarvis.vbs"

    vbs_content = (
        "' Jarvis X Living Core -- Silent Background Launcher\n"
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.CurrentDirectory = "{PROJECT_ROOT}"\n'
        f'WshShell.Run """{BAT_PATH}""", 0, False\n'
        "Set WshShell = Nothing\n"
    )
    vbs_path.write_text(vbs_content, encoding="utf-8")

    print("[SUCCESS] Created silent background launcher:")
    print(f"  VBS Launcher: {vbs_path}")
    print(f"  Batch Target: {BAT_PATH}")
    print()
    print("To run Jarvis X automatically on PC boot:")
    print("  1. Press Win + R, type 'shell:startup', press Enter.")
    print(f"  2. Right-click and paste a shortcut to: {vbs_path}")


if __name__ == "__main__":
    generate_desktop_launcher()
