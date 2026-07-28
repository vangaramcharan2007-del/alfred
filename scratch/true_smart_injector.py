import pyautogui
import pyperclip
import time
import win32gui

def get_active_window_title():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)

def run():
    print("[Jarvis X]: Monitoring active window. Please switch to the Swayam NPTEL tab now.")
    target_found = False
    for _ in range(120):
        title = get_active_window_title()
        if title:
            # ONLY trigger if the window is Swayam or Java course
            title_lower = title.lower()
            if 'swayam' in title_lower or 'java' in title_lower or 'nptel' in title_lower:
                # Make sure it's not our chat window
                if 'jarvis' not in title_lower and 'gemini' not in title_lower and 'chat' not in title_lower:
                    print(f"\n[Jarvis X]: TARGET ACQUIRED -> {title}")
                    target_found = True
                    break
        time.sleep(1)
        
    if not target_found:
        print("[Jarvis X]: Timed out.")
        return
        
    print("[Jarvis X]: Taking over in 3 seconds. DO NOT TOUCH MOUSE OR KEYBOARD.")
    time.sleep(3)
    
    # Open Console
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(3)
    
    # Type allow pasting
    pyautogui.write("allow pasting", interval=0.03)
    pyautogui.press('enter')
    time.sleep(1)
    
    js = "const a=['Use of pointers','Unicode escape sequence','Java Virtual Machine','int','char ch = \\'\\\\utea\\';','char ch = \\'\\\\u0021\\';','0','main method','32 bit','javac','interface','JDB','java.util','Marker Interface','java.lang.StringBuilder','java.lang.StringBuffer','Object','Applet','javap','Bytecode is executed by the JVM','Platform independent'];let c=0;const ls=Array.from(document.querySelectorAll('label,div,span,td'));a.forEach(t=>{for(let l of ls){if(l.innerText&&(l.innerText.trim()===t.trim()||l.innerText.includes(t))){let i=l.querySelector('input');if(!i&&l.getAttribute('for'))i=document.getElementById(l.getAttribute('for'));if(!i&&l.parentElement)i=l.parentElement.querySelector('input[type=\"radio\"],input[type=\"checkbox\"]');if(i){i.click();c++;break;}}}});setTimeout(()=>{const s=document.querySelector('button[type=\"submit\"],input[value=\"Submit\"],.gcb-button');if(s)s.click();},1000);"
    
    pyperclip.copy(js)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'shift', 'j') # close console
    print("[Jarvis X]: DONE. ASSIGNMENT DOMINATED.")

if __name__ == "__main__":
    run()
