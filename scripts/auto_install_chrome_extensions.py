"""
Jarvis X — Autonomous Chrome Extension Auto-Installer Bot.
Brings Chrome to focus and uses computer-use automation to click 'Add to Chrome' and confirm installation.
"""

import sys
import time
import subprocess
import pyautogui

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def focus_chrome():
    """Bring Google Chrome to foreground."""
    ps_cmd = "$w = New-Object -ComObject WScript.Shell; $w.AppActivate('Chrome')"
    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
    time.sleep(1.0)

def auto_install_tab(step_num: int):
    """Attempt to click Add to Chrome and confirm dialog for current tab."""
    print(f"[*] Processing Extension Tab #{step_num}...")
    
    # 1. Search for 'Add to Chrome' button or use targeted keyboard tab navigation
    # On Chrome Web Store, pressing '/' or tabbing to button or clicking the top-right blue area
    screen_w, screen_h = pyautogui.size()
    
    # Take screenshot of page to find blue 'Add to Chrome' button
    img = pyautogui.screenshot()
    
    # Find blue 'Add to Chrome' pill (#0b57d0 / #1a73e8) roughly in upper right quadrant
    found_btn = False
    target_x, target_y = None, None
    
    # Search between X: 1100 -> 1800, Y: 180 -> 450
    for y in range(180, min(500, screen_h), 8):
        for x in range(min(1100, screen_w - 600), screen_w - 100, 12):
            r, g, b = img.getpixel((x, y))[:3]
            # Chrome Web Store blue button: strong blue (B > 180, R < 80, G < 160)
            if b > 170 and r < 80 and g < 160:
                target_x, target_y = x, y
                found_btn = True
                break
        if found_btn:
            break
            
    if found_btn and target_x and target_y:
        print(f"    -> Located 'Add to Chrome' button at ({target_x}, {target_y}). Clicking...")
        pyautogui.click(target_x, target_y)
        time.sleep(1.5)
        
        # Confirmation Dialog appears at top center (around X=screen_w//2, Y=180-250)
        # Press Left + Enter or click 'Add extension'
        print("    -> Confirming 'Add extension' dialog...")
        pyautogui.press('left')
        time.sleep(0.3)
        pyautogui.press('enter')
        time.sleep(0.5)
        # Backup: click top center modal button position
        pyautogui.click(screen_w // 2, 220)
        time.sleep(2.0)
        
        # Close tab and move to next
        print("    -> Closing completed tab...")
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(1.0)
        return True
    else:
        print("    -> 'Add to Chrome' button already installed or not detected on this page.")
        # Move to next tab
        pyautogui.hotkey('ctrl', 'tab')
        time.sleep(1.0)
        return False

def main():
    print("\n" + "=" * 70)
    print("   ALFRED OS — AUTONOMOUS CHROME EXTENSION INSTALLER BOT")
    print("=" * 70 + "\n")
    
    print("[+] 1. Focusing Chrome...")
    focus_chrome()
    
    # Process up to 14 open tabs
    print("[+] 2. Iterating through open extension tabs...")
    for i in range(1, 15):
        auto_install_tab(i)
        
    print("\n" + "=" * 70)
    print("   AUTONOMOUS EXTENSION INSTALLATION SWEEP COMPLETE!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
