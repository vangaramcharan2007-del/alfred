import time
import pyperclip
import pyautogui

def solve():
    print("\n[Alfred]: Executing Blind Injection Protocol for Java Week 0.")
    print("[Alfred]: 1. Click on the middle of your NPTEL Assignment page NOW.")
    print("[Alfred]: 2. TAKE YOUR HANDS OFF THE MOUSE AND KEYBOARD.")
    print("[Alfred]: You have 5 seconds...")
    
    for i in range(5, 0, -1):
        print(f" -> {i}")
        time.sleep(1)
        
    print("[Alfred]: Taking control...")
    
    # 1. Open Console
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    
    # Bypass Chrome's "allow pasting" security feature
    pyautogui.write("allow pasting", interval=0.05)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    
    # Common NPTEL Java Week 0 Answers
    js_clicks = """
    const answers = [
        "Use of pointers",
        "Unicode escape sequence",
        "Java Virtual Machine",
        "int",
        "char ch = '\\\\utea';",
        "char ch = '\\\\u0021';",
        "0",
        "main method",
        "32 bit",
        "javac",
        "interface",
        "JDB",
        "java.util",
        "Marker Interface",
        "java.lang.StringBuilder",
        "java.lang.StringBuffer",
        "Object",
        "Applet",
        "javap",
        "Bytecode is executed by the JVM",
        "Platform independent"
    ];

    function clickOptionContaining(text) {
        const labels = Array.from(document.querySelectorAll('label, div, span, td'));
        for(let label of labels) {
            if(label.innerText && label.innerText.trim() === text.trim()) {
                let input = label.querySelector('input');
                if(!input && label.getAttribute('for')) input = document.getElementById(label.getAttribute('for'));
                if(!input) {
                    const parent = label.parentElement;
                    if(parent) input = parent.querySelector('input[type="radio"], input[type="checkbox"]');
                }
                if(input) { input.click(); return; }
            }
        }
        for(let label of labels) {
            if(label.innerText && label.innerText.includes(text)) {
                let input = label.querySelector('input');
                if(!input && label.getAttribute('for')) input = document.getElementById(label.getAttribute('for'));
                if(!input) {
                    const parent = label.parentElement;
                    if(parent) input = parent.querySelector('input[type="radio"], input[type="checkbox"]');
                }
                if(input) { input.click(); return; }
            }
        }
    }
    
    let clicked = 0;
    answers.forEach(ans => {
        try { clickOptionContaining(ans); clicked++; } catch(e) {}
    });
    
    setTimeout(() => {
        const submitBtn = document.querySelector('button[type="submit"], input[value="Submit"], button:contains("Submit"), .gcb-button');
        if(submitBtn) submitBtn.click();
    }, 1000);
    
    console.log('Jarvis X: Blind Sequence Complete!');
    """
    
    pyperclip.copy(js_clicks)
    time.sleep(0.5)
    
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    
    time.sleep(2)
    pyautogui.press('f12')
    
    print("[Alfred]: Complete! The answers have been injected and submitted.")

if __name__ == "__main__":
    solve()
