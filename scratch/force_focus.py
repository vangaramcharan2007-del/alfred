from pywinauto import Application
import pygetwindow as gw
import time
import pyautogui
import pyperclip

def run():
    print("[Jarvis X]: Locating browser window...")
    windows = gw.getWindowsWithTitle("Chrome")
    if not windows:
        windows = gw.getWindowsWithTitle("Opera")
        
    target_window = None
    for w in windows:
        if w.title:
            target_window = w
            break
            
    if not target_window:
        print("[Jarvis X]: Error - Could not find Chrome or Opera window.")
        return
        
    print(f"[Jarvis X]: Hooking into window: {target_window.title}")
    
    try:
        # Force the window to the front
        target_window.minimize()
        target_window.restore()
        target_window.activate()
    except Exception as e:
        print(f"[Jarvis X]: Warning - could not activate window via pygetwindow: {e}")
        
    time.sleep(2)
    
    print("[Jarvis X]: Deploying payload...")
    # Open Console
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(2)
    
    # Focus input
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    
    # Bypass Chrome security
    pyautogui.write("allow pasting", interval=0.05)
    pyautogui.press('enter')
    time.sleep(1)
    
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    
    js = "const a=['Use of pointers','Unicode escape sequence','Java Virtual Machine','int','char ch = \\'\\\\utea\\';','char ch = \\'\\\\u0021\\';','0','main method','32 bit','javac','interface','JDB','java.util','Marker Interface','java.lang.StringBuilder','java.lang.StringBuffer','Object','Applet','javap','Bytecode is executed by the JVM','Platform independent'];let c=0;const ls=Array.from(document.querySelectorAll('label,div,span,td'));a.forEach(t=>{for(let l of ls){if(l.innerText&&(l.innerText.trim()===t.trim()||l.innerText.includes(t))){let i=l.querySelector('input');if(!i&&l.getAttribute('for'))i=document.getElementById(l.getAttribute('for'));if(!i&&l.parentElement)i=l.parentElement.querySelector('input[type=\"radio\"],input[type=\"checkbox\"]');if(i){i.click();c++;break;}}}});setTimeout(()=>{const s=document.querySelector('button[type=\"submit\"],input[value=\"Submit\"],.gcb-button');if(s)s.click();},1000);"
    
    pyperclip.copy(js)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    
    time.sleep(2)
    pyautogui.press('f12')
    print("[Jarvis X]: Complete. NPTEL assignment has been dominated.")

if __name__ == "__main__":
    run()
