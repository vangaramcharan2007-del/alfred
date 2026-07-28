import pyautogui
import pyperclip
import time
import win32gui

def get_active_window_title():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)

def run():
    print("[Alfred]: Waiting for you to switch to the NPTEL assignment window...")
    print("[Alfred]: Please switch to your browser now. I will wait in the background...")
    
    target_found = False
    for _ in range(60): # Wait up to 60 seconds
        title = get_active_window_title().lower()
        if 'nptel' in title or 'java' in title or 'swayam' in title or 'chrome' in title or 'opera' in title or 'edge' in title or 'brave' in title:
            print(f"[Alfred]: Detected browser window: {title}")
            target_found = True
            break
        time.sleep(1)
        
    if not target_found:
        print("[Alfred]: Timed out waiting for browser window.")
        return
        
    print("[Alfred]: Target acquired! Waiting 3 seconds to ensure page is fully focused...")
    time.sleep(3)
    
    print("[Alfred]: Injecting...")
    # 1. Open Console
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(2.5)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    
    # Bypass Chrome/Opera "allow pasting" security feature
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
    print("[Alfred]: Done. The universal answers have been submitted.")

if __name__ == "__main__":
    run()
