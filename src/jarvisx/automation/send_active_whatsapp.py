"""
Direct Active WhatsApp Window Actuation for Charan.
Controls the already-open WhatsApp window on Windows:
1. Brings WhatsApp / Browser to foreground focus.
2. Searches for 'Dakshith'.
3. Types 'hello' and presses ENTER.
"""

import sys
import time
import subprocess
import pyautogui

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

pyautogui.FAILSAFE = False

print("\n[*] ==========================================================")
print("[*] ACTIVATING ON-SCREEN WHATSAPP DISPATCH TO DAKSHITH...")
print("[*] ==========================================================")


# 1. Bring WhatsApp / Chrome / Browser window to the foreground
ps_focus = """
$wshell = New-Object -ComObject WScript.Shell
$targets = @("WhatsApp", "Chrome", "Edge", "Brave", "Firefox")
foreach ($t in $targets) {
    if ($wshell.AppActivate($t)) {
        Write-Host "[+] Focused application: $t"
        break
    }
}
"""
subprocess.run(["powershell", "-NoProfile", "-Command", ps_focus], capture_output=True)
time.sleep(1.0)

# 2. Search for Dakshith
print("[*] Step 1: Navigating to search bar (Ctrl + F)...")
pyautogui.hotkey('ctrl', 'f')
time.sleep(0.6)

print("[*] Step 2: Typing contact name 'Dakshith'...")
pyautogui.write("Dakshith", interval=0.1)
time.sleep(1.2)

print("[*] Step 3: Selecting chat (Down + Enter)...")
pyautogui.press('down')
time.sleep(0.4)
pyautogui.press('enter')
time.sleep(1.0)

# 3. Type message and dispatch
print("[*] Step 4: Typing message 'hello'...")
pyautogui.write("hello", interval=0.08)
time.sleep(0.5)

print("[*] Step 5: Pressing ENTER to SEND message...")
pyautogui.press('enter')
time.sleep(0.5)

print("\n[OK] MESSAGE 'hello' DISPATCHED TO DAKSHITH IN YOUR ACTIVE WHATSAPP!")

