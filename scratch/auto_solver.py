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
    print("\n[Alfred]: Standing by. Please press Ctrl+A then Ctrl+C on your assignment page!")
    
    old_clip = pyperclip.paste()
    while True:
        current_clip = pyperclip.paste()
        if current_clip != old_clip and len(current_clip) > 100 and "Week 0" in current_clip or "NPTEL" in current_clip or "Assignment" in current_clip:
            print("[Alfred]: Assignment text detected in clipboard!")
            break
        time.sleep(1)
        
    assignment_text = current_clip
    
    if not HAS_GENAI:
        print("[Error]: Missing generativeai module.")
        return
        
    config_mgr = ConfigurationManager()
    config = config_mgr.get_config()
    api_key = config.get("providers", {}).get("llm", {}).get("gemini_api_key")
    genai.configure(api_key=api_key)
    
    print("[Alfred]: Computing answers using Jarvis X Core Intelligence (Gemini)...")
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    You are an expert Java programmer. The user has copied the text of their NPTEL Java Week 0 Assignment.
    Please read the questions and options.
    Output ONLY a valid JSON array of exactly the correct answer strings.
    For example, if the options for Q1 are "A) int", "B) void", and the answer is "int", output "int".
    Include enough of the string so we can uniquely match it on the page. Do not include 'A)' or 'B)'.
    
    Assignment Text:
    {assignment_text[:10000]}
    """
    
    response = model.generate_content(prompt)
    result_text = response.text.strip()
    
    if result_text.startswith("```json"):
        result_text = result_text.replace("```json", "").replace("```", "").strip()
    elif result_text.startswith("```"):
        result_text = result_text.replace("```", "").strip()
        
    answers = json.loads(result_text)
    print(f"[Alfred]: Computed {len(answers)} answers: {answers}")
    
    print("[Alfred]: Injecting clicks into your browser...")
    
    # Generate JS to click these answers
    js_clicks = """
    const answers = """ + json.dumps(answers) + """;
    function clickOptionContaining(text) {
        const labels = Array.from(document.querySelectorAll('label, div, span'));
        for(let label of labels) {
            if(label.innerText && label.innerText.trim() === text.trim()) {
                let input = label.querySelector('input');
                if(!input && label.getAttribute('for')) {
                    input = document.getElementById(label.getAttribute('for'));
                }
                if(!input) {
                    const parent = label.parentElement;
                    if(parent) input = parent.querySelector('input[type="radio"], input[type="checkbox"]');
                }
                if(input) {
                    input.click();
                    return;
                }
            }
        }
        // Fallback: substring match
        for(let label of labels) {
            if(label.innerText && label.innerText.includes(text)) {
                let input = label.querySelector('input');
                if(!input && label.getAttribute('for')) {
                    input = document.getElementById(label.getAttribute('for'));
                }
                if(!input) {
                    const parent = label.parentElement;
                    if(parent) input = parent.querySelector('input[type="radio"], input[type="checkbox"]');
                }
                if(input) {
                    input.click();
                    return;
                }
            }
        }
    }
    answers.forEach(clickOptionContaining);
    console.log('Jarvis X: Selected answers!');
    """
    
    pyperclip.copy(js_clicks)
    
    print("[Alfred]: Switch to your Chrome window and DO NOT touch the mouse!")
    time.sleep(3)
    
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('f12')
    
    print("[Alfred]: Complete! Please review the selections and submit.")

if __name__ == "__main__":
    solve()
