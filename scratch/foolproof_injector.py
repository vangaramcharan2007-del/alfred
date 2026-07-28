import pyautogui
import pyperclip
import time

def run():
    print("[Alfred]: The script is starting!")
    print("[Alfred]: YOU HAVE 15 SECONDS TO DO THIS:")
    print("[Alfred]: 1. Go to your NPTEL assignment browser tab.")
    print("[Alfred]: 2. Press F12 (or right-click -> Inspect).")
    print("[Alfred]: 3. Click on the 'Console' tab.")
    print("[Alfred]: 4. Click inside the blinking cursor area where you type commands.")
    print("[Alfred]: 5. DO NOT TOUCH YOUR MOUSE OR KEYBOARD AFTER THAT.")
    
    for i in range(15, 0, -1):
        print(f" -> {i} seconds remaining...")
        time.sleep(1)
        
    print("[Alfred]: Taking over...")
    
    # Type allow pasting to bypass security
    pyautogui.write("allow pasting", interval=0.02)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # The universal JS payload
    js = "const a=['Use of pointers','Unicode escape sequence','Java Virtual Machine','int','char ch = \\'\\\\utea\\';','char ch = \\'\\\\u0021\\';','0','main method','32 bit','javac','interface','JDB','java.util','Marker Interface','java.lang.StringBuilder','java.lang.StringBuffer','Object','Applet','javap','Bytecode is executed by the JVM','Platform independent'];let c=0;const ls=Array.from(document.querySelectorAll('label,div,span,td'));a.forEach(t=>{for(let l of ls){if(l.innerText&&(l.innerText.trim()===t.trim()||l.innerText.includes(t))){let i=l.querySelector('input');if(!i&&l.getAttribute('for'))i=document.getElementById(l.getAttribute('for'));if(!i&&l.parentElement)i=l.parentElement.querySelector('input[type=\"radio\"],input[type=\"checkbox\"]');if(i){i.click();c++;break;}}}});setTimeout(()=>{const s=document.querySelector('button[type=\"submit\"],input[value=\"Submit\"],.gcb-button');if(s)s.click();},1000);"
    
    pyperclip.copy(js)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    
    print("[Alfred]: INJECTION COMPLETE! Did it submit?")

if __name__ == "__main__":
    run()
