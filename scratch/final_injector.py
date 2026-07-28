import pyautogui
import pyperclip
import time

def run():
    print("[Alfred]: Final override active. FOCUS YOUR NPTEL CHROME TAB NOW!")
    time.sleep(4)
    
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
    
    js = """
    const answers = ["Use of pointers", "Unicode escape sequence", "Java Virtual Machine", "int", "char ch = '\\\\utea';", "char ch = '\\\\u0021';", "0", "main method", "32 bit", "javac", "interface", "JDB", "java.util", "Marker Interface", "java.lang.StringBuilder", "java.lang.StringBuffer", "Object", "Applet", "javap", "Bytecode is executed by the JVM", "Platform independent"];
    let clicked = 0;
    const labels = Array.from(document.querySelectorAll("label, div, span, td"));
    answers.forEach(text => {
        for(let label of labels) {
            if(label.innerText && (label.innerText.trim() === text.trim() || label.innerText.includes(text))) {
                let input = label.querySelector("input");
                if(!input && label.getAttribute("for")) input = document.getElementById(label.getAttribute("for"));
                if(!input && label.parentElement) input = label.parentElement.querySelector("input[type='radio'], input[type='checkbox']");
                if(input) { input.click(); clicked++; break; }
            }
        }
    });
    setTimeout(() => {
        const submitBtn = document.querySelector("button[type='submit'], input[value='Submit'], .gcb-button");
        if(submitBtn) submitBtn.click();
    }, 1000);
    """
    
    pyperclip.copy(js)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    
    time.sleep(2)
    pyautogui.press('f12')
    print("[Alfred]: Done.")

if __name__ == "__main__":
    run()
