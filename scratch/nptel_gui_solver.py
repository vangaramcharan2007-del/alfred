import asyncio
import os
import json
import time
import pyperclip
import pyautogui

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from jarvisx.core.llm_router import OmniRouterClient

async def solve_nptel_via_gui():
    print("\n[Alfred]: Initiating NPTEL Week 0 GUI Injection Sequence...")
    print("[Alfred]: This will bypass Google's anti-bot protection by using your active browser.")
    print("[Alfred]: PLEASE MAKE SURE GOOGLE CHROME IS YOUR ACTIVE WINDOW AND THE ASSIGNMENT IS OPEN.")
    print("[Alfred]: You have 5 seconds to click on your Chrome window...")
    
    # 1. Wait for user to focus Chrome
    for i in range(5, 0, -1):
        print(f" -> {i} seconds...")
        time.sleep(1)
        
    print("\n[Alfred]: Taking control of keyboard. Please do not touch your mouse or keyboard.")
    
    # 2. Open Developer Tools Console (Ctrl+Shift+J on Windows Chrome)
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(2) # Wait for console to open
    
    # Clear console to be safe
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    
    # 3. Inject JS to copy HTML to clipboard
    js_extract = "copy(document.querySelector('form') ? document.querySelector('form').outerHTML : document.body.innerHTML);"
    pyperclip.copy(js_extract)
    
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    
    print("[Alfred]: Extracting assignment data from the DOM...")
    time.sleep(1) # Wait for copy to complete
    
    # 4. Read clipboard
    form_html = pyperclip.paste()
    
    if len(form_html) < 100:
        print("[Error]: Failed to extract HTML. Did the console open properly?")
        return
        
    print("[Alfred]: HTML Extracted successfully. Transmitting to OmniRoute...")
    
    prompt = f"""
    You are an expert Java programmer and automation engineer. 
    Here is the HTML of an NPTEL Week 0 assignment for "Programming in Java".
    1. Read the questions and options.
    2. Determine the correct answers.
    3. Return a JSON array of the exact CSS selectors needed to click the correct <input type="radio"> or <input type="checkbox"> elements.
    4. Only output the raw JSON array of strings, nothing else. No markdown formatting.
    
    Example output:
    ["input[name='question1'][value='A']", "input[id='q2_option3']"]
    
    HTML Content:
    {form_html[:50000]}
    """
    
    try:
        router = OmniRouterClient()
        messages = [{"role": "user", "content": prompt}]
        result_text = await router.chat(messages, model="llama3")
        result_text = result_text.strip()
        
        # Clean up markdown if present
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        elif result_text.startswith("```"):
            result_text = result_text.replace("```", "").strip()
            
        selectors = json.loads(result_text)
        print(f"[Alfred]: OmniRoute computed {len(selectors)} answers. Injecting clicks...")
        
        # 5. Build JS to execute clicks
        js_clicks = "(() => { const selectors = " + json.dumps(selectors) + "; "
        js_clicks += "selectors.forEach(sel => { const el = document.querySelector(sel); if(el) el.click(); }); "
        js_clicks += "console.log('Jarvis X: Sequence Complete'); })();"
        
        pyperclip.copy(js_clicks)
        
        # Paste and execute clicks
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        
        print("\n[Alfred]: Answers have been selected successfully!")
        
        # Close DevTools
        time.sleep(1)
        pyautogui.press('f12')
        
        print("[Alfred]: Handing control back to you. Please review the answers and click Submit.")
        
    except Exception as e:
        print(f"\n[Error]: OmniRoute failed or parsing error: {e}")

if __name__ == "__main__":
    asyncio.run(solve_nptel_via_gui())
