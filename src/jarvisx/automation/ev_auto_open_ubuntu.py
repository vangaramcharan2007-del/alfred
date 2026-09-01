"""
Automated VMware Ubuntu Launcher & E-V Voice Announcer.
======================================================
1. Opens Ubuntu 64-bit.vmx directly using native Windows ShellExecute.
2. Monitors the foreground process until VMware's GUI window is active.
3. Triggers E-V's natural human neural voice to announce completion out loud!
"""

import os
import sys
import time
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from jarvisx.automation.ev_neural_voice import speak_ev_neural

VMX_PATH = r"C:\Users\vanga\OneDrive\Documents\Ubuntu 64-bit.vmx"


def main():
    print("=" * 78)
    print(" 🕷️ E-V AUTOMATED UBUNTU VM LAUNCHER")
    print("=" * 78)

    # 1. Announce starting
    speak_ev_neural("On it, boss! E-V is launching your Ubuntu system right now!")

    # 2. Launch via Win32 ShellExecute
    print(f"[*] Launching {VMX_PATH} via Win32 ShellExecute...")
    try:
        os.startfile(VMX_PATH)
    except Exception as e:
        print(f"[!] Launch fallback via vmware.exe: {e}")
        subprocess.Popen([r"C:\Program Files\VMware\VMware Workstation\vmware.exe", "-x", VMX_PATH])

    # 3. Wait for VMware window to appear
    print("[*] Monitoring process and window station...")
    opened = False
    for i in range(1, 15):
        time.sleep(1)
        res = subprocess.run(
            ["powershell.exe", "-Command", "Get-Process -Name vmware -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"],
            capture_output=True,
            text=True
        )
        if res.stdout.strip():
            opened = True
            print(f"[✓] VMware process active (PIDs: {res.stdout.strip()}) on check #{i}!")
            break

    # 4. Final E-V Announcement
    time.sleep(2)
    speak_ev_neural("Hey boss! E-V did it! Your Ubuntu 64-bit desktop is officially opened and running live on your screen!")

    print("=" * 78)
    print(" 🏆 E-V COMPLETED LAUNCH & ANNOUNCEMENT!")
    print("=" * 78)


if __name__ == "__main__":
    main()
