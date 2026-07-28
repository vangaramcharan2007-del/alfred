import time
import pyperclip
import pyautogui
import os

def extract():
    print("\n[Alfred]: Preparing to extract HTML...")
    print("[Alfred]: FOCUS CHROME NOW! You have 5 seconds...")
    for i in range(5, 0, -1):
        print(f" -> {i}")
        time.sleep(1)
        
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    
    js_extract = "copy(document.querySelector('form') ? document.querySelector('form').outerHTML : document.body.innerHTML);"
    pyperclip.copy(js_extract)
    
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    
    time.sleep(1)
    form_html = pyperclip.paste()
    
    with open(os.path.join(os.path.dirname(__file__), "nptel_form.html"), "w", encoding="utf-8") as f:
        f.write(form_html)
    
    print("[Alfred]: Extraction complete! Handing over to Jarvis X Core.")
    
    # Close DevTools
    pyautogui.press('f12')

if __name__ == "__main__":
    extract()
