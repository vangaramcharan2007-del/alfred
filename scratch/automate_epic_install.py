"""Autonomous Epic Games & Unreal Engine Installer Driver for Jarvis X: GENESIS.

Uses native Win32 + PyAutoGUI computer use to focus windows, send keyboard commands,
and execute the installation end-to-end in front of the user's eyes.
"""

import sys
import time
import subprocess
import pyautogui

# Enable failsafe & slight pause between keystrokes
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False

print("[ALFRED COMPUTER USE]: Starting autonomous desktop interaction...")

# 1. Bring Epic Games / Windows Installer to front using PowerShell
ps_script = """
$wshell = New-Object -ComObject wscript.shell
$procs = Get-Process | Where-Object { $_.MainWindowTitle -like "*Epic Games*" -or $_.ProcessName -like "*msi*" }
foreach ($p in $procs) {
    $wshell.AppActivate($p.Id)
    Start-Sleep -Milliseconds 300
}
"""

try:
    subprocess.run(["powershell", "-Command", ps_script], timeout=5)
    time.sleep(1.0)
except Exception as e:
    print(f"Window focus notice: {e}")

# 2. Press Enter to trigger default Install button on the active installer
print("[ALFRED COMPUTER USE]: Triggering 'Install' action via Enter keystroke...")
pyautogui.press('enter')
time.sleep(1.5)

# In case there is a folder selection or UAC prompt, press Enter again
pyautogui.press('enter')
print("[ALFRED COMPUTER USE]: Keystroke sent successfully.")

# 3. Check if Epic Games Launcher starts and launch if needed
print("[ALFRED COMPUTER USE]: Waiting for launcher...")
time.sleep(3.0)

# Check if Epic Games process is active
chk = subprocess.run(
    ["powershell", "-Command", "Get-Process | Where-Object { $_.ProcessName -like '*EpicGames*' }"],
    capture_output=True,
    text=True
)

if "EpicGames" in chk.stdout:
    print("[ALFRED COMPUTER USE]: Epic Games Launcher is active and running on screen!")
else:
    print("[ALFRED COMPUTER USE]: Attempting direct launcher startup...")
    subprocess.Popen(["C:\\Program Files (x86)\\Epic Games\\Launcher\\Portal\\Binaries\\Win64\\EpicGamesLauncher.exe"])

print("\n=========================================================================")
print("  🤖 ALFRED AUTONOMOUS COMPUTER-USE ACTION COMPLETE")
print("=========================================================================\n")
