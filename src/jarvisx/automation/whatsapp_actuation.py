"""
WhatsApp Visual Desktop & Web Actuation Engine for Jarvis X.
Executes live on-screen WhatsApp messaging right in front of Charan's eyes:
1. Deep links to WhatsApp Desktop (`whatsapp://`) and WhatsApp Web (`https://web.whatsapp.com`).
2. Automates contact lookup, message composition, and Enter key dispatch via Windows Shell / PyAutoGUI.
"""

import os
import subprocess
import sys
import time
import urllib.parse
import webbrowser
import logging

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger("jarvisx.whatsapp")


def send_whatsapp_live(recipient: str = "Dakshith", message: str = "hi") -> dict:
    """
    Executes on-screen WhatsApp automation to send a message.
    """
    print(f"\n[WHATSAPP ACTUATION] [*] Initiating on-screen message dispatch to '{recipient}' with text: '{message}'...")
    encoded_msg = urllib.parse.quote(message)
    
    # Direct phone vs contact name
    is_phone_num = "".join(filter(str.isdigit, recipient))
    if len(is_phone_num) >= 10:
        url = f"https://web.whatsapp.com/send?phone={is_phone_num}&text={encoded_msg}"
        desktop_protocol = f"whatsapp://send?phone={is_phone_num}&text={encoded_msg}"
    else:
        url = f"https://web.whatsapp.com/send?text={encoded_msg}"
        desktop_protocol = f"whatsapp://send?text={encoded_msg}"

    print(f"[*] Launching WhatsApp on your screen...")
    
    # 1. Try Windows native protocol & browser launch
    try:
        os.system(f'start "" "{desktop_protocol}"')
    except Exception:
        pass

    
    webbrowser.open(url)

    # 2. Windows Native PowerShell WScript.Shell SendKeys Automation
    print("[*] Waiting 3 seconds for WhatsApp window to focus...")
    time.sleep(3.0)

    try:
        # PowerShell SendKeys script to automate search, select, type message and press Enter
        ps_script = f"""
$wshell = New-Object -ComObject WScript.Shell
Start-Sleep -Milliseconds 800
# Focus and search for contact if name
$wshell.SendKeys('^f')
Start-Sleep -Milliseconds 500
$wshell.SendKeys('{recipient}')
Start-Sleep -Milliseconds 1200
$wshell.SendKeys('{{DOWN}}')
Start-Sleep -Milliseconds 300
$wshell.SendKeys('{{ENTER}}')
Start-Sleep -Milliseconds 800
# Type message and press Enter
$wshell.SendKeys('{message}')
Start-Sleep -Milliseconds 400
$wshell.SendKeys('{{ENTER}}')
"""
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], timeout=10)
        print(f"\n[WHATSAPP ACTUATION] [OK] Live keystrokes executed on-screen for '{recipient}': '{message}'!")
        return {
            "status": "DISPATCHED_LIVE",
            "recipient": recipient,
            "message": message,
            "mode": "WINDOWS_SHELL_SENDKEYS"
        }
    except Exception as e:
        print(f"[*] SendKeys note: {e}")
        return {
            "status": "DISPATCHED_BROWSER",
            "recipient": recipient,
            "message": message,
            "url": url
        }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Dakshith"
    msg = sys.argv[2] if len(sys.argv) > 2 else "hi"
    send_whatsapp_live(target, msg)
