import time
import pyperclip
import pyautogui
import os
import json

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from jarvisx.core.configuration import ConfigurationManager

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def solve():
    print("\n[Alfred]: NPTEL Anti-Copy protection detected. Engaging override protocol.")
    print("[Alfred]: 1. Click on the middle of your NPTEL Assignment page NOW.")
    print("[Alfred]: 2. TAKE YOUR HANDS OFF THE MOUSE AND KEYBOARD.")
    print("[Alfred]: You have 5 seconds...")
    
    for i in range(5, 0, -1):
        print(f" -> {i}")
        time.sleep(1)
        
    print("[Alfred]: Taking control...")
    
    # 1. Open Console
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(2.5) # Wait for console
    
    # 2. Clear console
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    
    # 3. Inject JS to programmatically copy the page text (bypasses CSS/JS copy blocks)
    js_extract = "copy(Array.from(document.querySelectorAll('.qt-question, .question-wrapper, .gcb-question-row, form')).map(e => e.innerText).join('\\n\\n'));"
    pyperclip.copy(js_extract)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    
    print("[Alfred]: Extracted protected text. Processing with Gemini...")
    time.sleep(1.5) # Wait for copy to execute
    
    assignment_text = pyperclip.paste()
    
    if len(assignment_text) < 50:
        print("[Error]: Failed to extract text. Console might not have opened correctly.")
        return
        
    with open(os.path.join(os.path.dirname(__file__), "nptel_text.txt"), "w", encoding="utf-8") as f:
        f.write(assignment_text)
        
    print("[Alfred]: Extraction complete! Antigravity will now process it.")

if __name__ == "__main__":
    solve()
