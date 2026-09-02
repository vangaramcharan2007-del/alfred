"""
Alfred OS Windows Startup & Auto-Boot Persistence Installer.
Ensures Alfred Master OS (Wake-Word Listener, Game Governor, Live Code Auto-Pilot, Situation Room)
automatically and silently boots the moment your laptop powers on and logs into Windows.
"""

from __future__ import annotations

import os
import subprocess
import sys
import winreg
from pathlib import Path
from typing import Dict, Any

# Ensure UTF-8 console output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Root project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
VENV_PYTHONW = PROJECT_ROOT / ".venv" / "Scripts" / "pythonw.exe"
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

# If pythonw.exe doesn't exist, fallback to python.exe
PYTHON_EXEC = VENV_PYTHONW if VENV_PYTHONW.exists() else (sys.executable if "pythonw" in sys.executable else VENV_PYTHON)

STARTUP_DIR = Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"))
VBS_LAUNCHER = STARTUP_DIR / "AlfredMasterOS.vbs"
BAT_LAUNCHER = STARTUP_DIR / "AlfredMasterOS.bat"


class WindowsAutoBootInstaller:
    """Manages automatic startup persistence across Windows Startup folder, Registry, and Task Scheduler."""

    @staticmethod
    def install_startup_persistence() -> Dict[str, Any]:
        """Installs the silent auto-boot triggers across all 3 Windows startup layers."""
        STARTUP_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Create Silent VBScript in Startup Folder
        # WScript.Shell.Run with parameter '0' ensures NO black command prompt window appears
        vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{PROJECT_ROOT}"
WshShell.Run """{PYTHON_EXEC}""" & " -m jarvisx live", 0, False
Set WshShell = Nothing
'''
        with open(VBS_LAUNCHER, "w", encoding="utf-8") as f:
            f.write(vbs_content)

        # 2. Add to Windows Registry Run Key (HKCU\Software\Microsoft\Windows\CurrentVersion\Run)
        reg_status = "FAILED"
        try:
            reg_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(
                reg_key,
                "AlfredMasterOS",
                0,
                winreg.REG_SZ,
                f'wscript.exe "{VBS_LAUNCHER}"'
            )
            winreg.CloseKey(reg_key)
            reg_status = "REGISTERED"
        except Exception as e:
            reg_status = f"REG_ERROR: {e}"

        # 3. Register with Windows Task Scheduler (schtasks) for instant boot at logon
        task_name = "AlfredMasterOS_AutoBoot"
        schtasks_status = "FAILED"
        try:
            # Delete any existing task
            subprocess.run(
                ["schtasks", "/delete", "/tn", task_name, "/f"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Create new task triggered at logon
            cmd = [
                "schtasks",
                "/create",
                "/tn", task_name,
                "/tr", f'wscript.exe "{VBS_LAUNCHER}"',
                "/sc", "onlogon",
                "/rl", "HIGHEST",
                "/f"
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                schtasks_status = "REGISTERED (ONLOGON)"
            else:
                # Fallback to least privilege if HIGHEST needs elevation
                cmd[cmd.index("HIGHEST")] = "LIMITED"
                res2 = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                schtasks_status = "REGISTERED (LIMITED)" if res2.returncode == 0 else f"ERROR: {res2.stderr.strip()}"
        except Exception as ex:
            schtasks_status = f"SCHTASKS_ERROR: {ex}"

        return {
            "vbs_launcher": str(VBS_LAUNCHER),
            "vbs_exists": VBS_LAUNCHER.exists(),
            "registry_run_key": reg_status,
            "task_scheduler": schtasks_status,
            "python_executable": str(PYTHON_EXEC),
            "project_root": str(PROJECT_ROOT),
        }

    @staticmethod
    def uninstall_startup_persistence() -> Dict[str, Any]:
        """Removes all auto-boot entries."""
        # 1. Remove VBS / BAT from Startup folder
        if VBS_LAUNCHER.exists():
            VBS_LAUNCHER.unlink()
        if BAT_LAUNCHER.exists():
            BAT_LAUNCHER.unlink()

        # 2. Remove Registry Key
        try:
            reg_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(reg_key, "AlfredMasterOS")
            winreg.CloseKey(reg_key)
        except Exception:
            pass

        # 3. Delete Scheduled Task
        try:
            subprocess.run(["schtasks", "/delete", "/tn", "AlfredMasterOS_AutoBoot", "/f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:
            pass

        return {"status": "UNINSTALLED"}

    @staticmethod
    def check_status() -> Dict[str, Any]:
        """Checks if auto-boot is currently active."""
        vbs_installed = VBS_LAUNCHER.exists()
        
        reg_installed = False
        try:
            reg_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            val, _ = winreg.QueryValueEx(reg_key, "AlfredMasterOS")
            reg_installed = bool(val)
            winreg.CloseKey(reg_key)
        except Exception:
            reg_installed = False

        return {
            "vbs_in_startup_folder": vbs_installed,
            "registry_run_key_active": reg_installed,
            "auto_boot_enabled": vbs_installed or reg_installed,
            "startup_file_path": str(VBS_LAUNCHER)
        }


if __name__ == "__main__":
    print("\n" + "=" * 75)
    print(" 🚀 INSTALLING ALFRED OS WINDOWS AUTO-BOOT PERSISTENCE")
    print("=" * 75)
    result = WindowsAutoBootInstaller.install_startup_persistence()
    print(f" [+] Startup Folder VBS : {result['vbs_launcher']} (Created: {result['vbs_exists']})")
    print(f" [+] Registry Run Key   : {result['registry_run_key']}")
    print(f" [+] Task Scheduler     : {result['task_scheduler']}")
    print("\n [OK] ✅ Alfred will now automatically start in the background every time you turn on your laptop!")
    print("=" * 75 + "\n")
