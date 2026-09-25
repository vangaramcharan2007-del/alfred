#!/usr/bin/env python3
"""
Jarvis X - Agent Mike Windows Silent Startup Installer (Option 4)
Registers a windowless VBScript launcher in the Windows Startup folder:
%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\JarvisAgentMikeStartup.vbs

Runs pythonw.exe completely in the background:
- 0 terminal window popups
- 0 console flash
- <0.01% idle CPU footprint
- Instant dynamic chameleon theming and global hotkey (Win+Alt+C) on system login
"""

import os
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STARTUP_DIR = Path(os.environ["APPDATA"]) / r"Microsoft\Windows\Start Menu\Programs\Startup"
VBS_FILE = STARTUP_DIR / "JarvisAgentMikeStartup.vbs"
CUSTOMIZER_SCRIPT = PROJECT_ROOT / "scripts" / "agent_mike_customizer.py"


def get_pythonw_path() -> Path:
    py_dir = Path(sys.executable).parent
    pythonw = py_dir / "pythonw.exe"
    if pythonw.exists():
        return pythonw
    return Path(sys.executable)


def install_startup():
    pythonw = get_pythonw_path()
    if not STARTUP_DIR.exists():
        STARTUP_DIR.mkdir(parents=True, exist_ok=True)

    vbs_content = (
        "' ==============================================================================\n"
        "' JARVIS X - AGENT MIKE SILENT BACKGROUND STARTUP LAUNCHER\n"
        "' Launches PC Customizer Daemon & Win+Alt+C Global Hotkey Listener headlessly.\n"
        "' Zero console window popups, zero UI clutter, <0.01% CPU profile.\n"
        "' ==============================================================================\n"
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.Run """{pythonw}"" ""{CUSTOMIZER_SCRIPT}"" --daemon", 0, False\n'
    )

    with open(VBS_FILE, "w", encoding="utf-8") as f:
        f.write(vbs_content)

    print("=" * 70)
    print("  JARVIS X - AGENT MIKE WINDOWS SILENT STARTUP INSTALLER")
    print("=" * 70)
    print(f"[+] Successfully installed silent launcher:")
    print(f"    Target File   : {VBS_FILE}")
    print(f"    Binary        : {pythonw}")
    print(f"    Script Target : {CUSTOMIZER_SCRIPT}")
    print(f"    Mode          : Headless pythonw.exe (0 console windows, 0 taskbar entries)")
    print(f"    Status        : Enabled for Windows Startup on login.")
    return True


def uninstall_startup():
    if VBS_FILE.exists():
        VBS_FILE.unlink()
        print(f"[+] Uninstalled JarvisAgentMikeStartup from Windows Startup: {VBS_FILE}")
    else:
        print(f"[i] Startup file does not exist: {VBS_FILE}")
    return True


def check_status():
    installed = VBS_FILE.exists()
    print("=" * 70)
    print("  JARVIS X - AGENT MIKE STARTUP STATUS")
    print("=" * 70)
    print(f"    Startup File : {VBS_FILE}")
    print(f"    Installed    : {'YES (Active on Boot)' if installed else 'NO'}")
    if installed:
        print(f"    Size         : {VBS_FILE.stat().st_size} bytes")
    return installed


def main():
    parser = argparse.ArgumentParser(description="Jarvis X Agent Mike Startup Manager")
    parser.add_argument("--install", action="store_true", help="Install to Windows Startup")
    parser.add_argument("--uninstall", action="store_true", help="Remove from Windows Startup")
    parser.add_argument("--status", action="store_true", help="Check installation status")

    args = parser.parse_args()

    if args.uninstall:
        uninstall_startup()
    elif args.status:
        check_status()
    else:
        # Default action is install
        install_startup()


if __name__ == "__main__":
    main()
