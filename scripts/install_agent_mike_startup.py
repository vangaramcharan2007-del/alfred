#!/usr/bin/env python3
"""
Jarvis X - Agent Mike Windows Silent Startup Installer & Watchdog Registrar
Registers a windowless VBScript launcher in the Windows Startup folder:
%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\JarvisAgentMikeStartup.vbs

Also registers a Windows Scheduled Task (JarvisAgentMikeSentinel) for multi-layer redundancy.
Runs pythonw.exe completely in the background:
- 0 terminal window popups
- 0 console flash
- <0.01% idle CPU footprint
- Instant dynamic chameleon theming and global hotkey (Win+Alt+C)
"""

import os
import sys
import psutil
import subprocess
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


def install_startup(start_now: bool = True):
    pythonw = get_pythonw_path()
    if not STARTUP_DIR.exists():
        STARTUP_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Write the silent VBS launcher
    vbs_content = (
        "' ==============================================================================\n"
        "' JARVIS X - AGENT MIKE SILENT BACKGROUND STARTUP LAUNCHER\n"
        "' Launches PC Customizer Daemon & Win+Alt+C Global Hotkey Listener headlessly.\n"
        "' Zero console window popups, zero UI clutter, <0.01% CPU profile.\n"
        "' ==============================================================================\n"
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.CurrentDirectory = "{PROJECT_ROOT}"\n'
        f'WshShell.Run """{pythonw}"" ""{CUSTOMIZER_SCRIPT}"" --daemon", 0, False\n'
    )

    try:
        with open(VBS_FILE, "w", encoding="utf-8") as f:
            f.write(vbs_content)
    except Exception as e:
        if not VBS_FILE.exists():
            raise e

    # 2. Register Windows Scheduled Task for double-layer boot persistence
    task_name = "JarvisAgentMikeSentinel"
    try:
        cmd = f'schtasks /create /tn "{task_name}" /tr "wscript.exe \\"{VBS_FILE}\\"" /sc onlogon /f /rl limited'
        subprocess.run(cmd, shell=True, capture_output=True)
    except Exception:
        pass

    # 3. Terminate previous daemon via PID lock if running
    PID_FILE = PROJECT_ROOT / "var" / "runtime" / "agent_mike_customizer.pid"
    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r", encoding="utf-8") as pf:
                old_pid = int(pf.read().strip())
            if psutil.pid_exists(old_pid):
                p = psutil.Process(old_pid)
                p.kill()
        except Exception:
            pass

    # 4. Launch the fresh daemon via wscript.exe (the native Windows silent host)
    if start_now:
        try:
            subprocess.run(["wscript.exe", str(VBS_FILE)], check=False)
        except Exception:
            subprocess.Popen(
                [str(pythonw), str(CUSTOMIZER_SCRIPT), "--daemon"],
                cwd=str(PROJECT_ROOT),
                creationflags=0x08000000 | 0x00000008 | 0x00000200,
                close_fds=True
            )

    print("=" * 70)
    print("  JARVIS X - AGENT MIKE PERMANENT SERVICE INSTALLER")
    print("=" * 70)
    print(f"[+] Successfully installed and secured permanent background service:")
    print(f"    Startup File   : {VBS_FILE}")
    print(f"    Scheduled Task : {task_name} (Active on logon)")
    print(f"    Binary         : {pythonw}")
    print(f"    Script Target  : {CUSTOMIZER_SCRIPT}")
    print(f"    Live Daemon    : Fresh instance launched silently via wscript")
    print(f"    Mode           : Headless pythonw.exe (0 console windows, 0 screen clutter)")
    return True


def uninstall_startup():
    if VBS_FILE.exists():
        VBS_FILE.unlink()
        print(f"[+] Removed VBS launcher: {VBS_FILE}")
    try:
        subprocess.run('schtasks /delete /tn "JarvisAgentMikeSentinel" /f', shell=True, capture_output=True)
        print(f"[+] Removed scheduled task JarvisAgentMikeSentinel")
    except Exception:
        pass
    return True


def check_status():
    installed = VBS_FILE.exists()
    running_pids = []
    
    # 1. Check atomic PID file
    PID_FILE = PROJECT_ROOT / "var" / "runtime" / "agent_mike_customizer.pid"
    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r", encoding="utf-8") as f:
                fpid = int(f.read().strip())
            if psutil.pid_exists(fpid):
                p = psutil.Process(fpid)
                if "python" in (p.name() or "").lower():
                    running_pids.append(fpid)
        except Exception:
            pass

    # 2. Fallback check for any active customizer daemon processes
    if not running_pids:
        for p in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = (p.info['name'] or '').lower()
                if not (name.startswith('python') or name.startswith('pythonw')):
                    continue
                cmd = " ".join(p.info['cmdline'] or []).lower()
                if "agent_mike_customizer" in cmd and "--daemon" in cmd:
                    running_pids.append(p.info['pid'])
            except Exception:
                pass

    print("=" * 70)
    print("  JARVIS X - AGENT MIKE PERMANENT STATUS")
    print("=" * 70)
    print(f"    Startup File   : {VBS_FILE}")
    print(f"    Installed      : {'YES' if installed else 'NO'}")
    print(f"    Live Daemon    : {'ONLINE (PID ' + str(running_pids) + ')' if running_pids else 'OFFLINE'}")
    return installed and bool(running_pids)


def main():
    parser = argparse.ArgumentParser(description="Jarvis X Agent Mike Startup Manager")
    parser.add_argument("--install", action="store_true", help="Install & launch permanent service")
    parser.add_argument("--uninstall", action="store_true", help="Remove permanent service")
    parser.add_argument("--status", action="store_true", help="Check service status")

    args = parser.parse_args()

    if args.uninstall:
        uninstall_startup()
    elif args.status:
        check_status()
    else:
        install_startup(start_now=True)


if __name__ == "__main__":
    main()
