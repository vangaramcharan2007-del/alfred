import sys
import os

with open(r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\src\jarvisx\agents\friday.py", "r") as f:
    code = f.read()

# 1. Manage terminal focus manually for the first execution block
old_exec1 = """                    vscode.vscode_run_in_terminal(f"python {target_script1}")
                    result1 = subprocess.run(["python", target_script1], capture_output=True, text=True)
                    
                    vscode.vscode_run_in_terminal(f"python {target_script2}")
                    result2 = subprocess.run(["python", target_script2], capture_output=True, text=True)"""

new_exec1 = """                    import pyautogui
                    # Open terminal
                    pyautogui.hotkey("ctrl", "`")
                    import time; time.sleep(1.0)
                    
                    vscode.vscode_run_in_terminal(f"python {target_script1}")
                    result1 = subprocess.run(["python", target_script1], capture_output=True, text=True)
                    
                    vscode.vscode_run_in_terminal(f"python {target_script2}")
                    result2 = subprocess.run(["python", target_script2], capture_output=True, text=True)"""

code = code.replace(old_exec1, new_exec1)

# 2. Focus the editor before correcting the code!
old_correct = """                        import pyautogui, time
                        pyautogui.hotkey("ctrl", "a")
                        time.sleep(0.1)
                        pyautogui.press("backspace")
                        vscode.vscode_type_code(corrected_code)
                        vscode.vscode_save()"""
                        
new_correct = """                        import pyautogui, time
                        # Focus the editor area first before selecting all!
                        pyautogui.hotkey("ctrl", "1")
                        time.sleep(0.5)
                        
                        pyautogui.hotkey("ctrl", "a")
                        time.sleep(0.1)
                        pyautogui.press("backspace")
                        vscode.vscode_type_code(corrected_code)
                        vscode.vscode_save()"""

code = code.replace(old_correct, new_correct)

# 3. Focus the terminal again before re-executing
old_exec2 = """                        result = subprocess.run(["python", os.path.join(target_path, "numpy_random.py")], capture_output=True, text=True)
                        vscode.vscode_run_in_terminal(f"python {os.path.join(target_path, 'numpy_random.py')}")"""
                        
new_exec2 = """                        result = subprocess.run(["python", os.path.join(target_path, "numpy_random.py")], capture_output=True, text=True)
                        # Re-focus the terminal by clicking terminal toggle twice (close then open)
                        pyautogui.hotkey("ctrl", "`")
                        time.sleep(0.5)
                        pyautogui.hotkey("ctrl", "`")
                        time.sleep(0.5)
                        vscode.vscode_run_in_terminal(f"python {os.path.join(target_path, 'numpy_random.py')}")"""
                        
code = code.replace(old_exec2, new_exec2)

# 4. Bulletproof Notepad
old_notepad = """                    import subprocess, time
                    import pygetwindow as gw
                    
                    # Launch notepad explicitly
                    subprocess.Popen(['notepad.exe'])
                    time.sleep(2.0)
                    
                    # Force window activation
                    try:
                        for win in gw.getWindowsWithTitle('Notepad'):
                            win.activate()
                            break
                    except Exception as e:
                        print(f"Window activation fallback: {e}")
                    
                    time.sleep(1.0)
                    vscode.vscode_type_code(explanation_text)"""
                    
new_notepad = """                    import os, time
                    import pygetwindow as gw
                    
                    # Use start to force OS window creation
                    os.system("start notepad")
                    time.sleep(1.5)
                    
                    # Force window activation just in case
                    try:
                        for win in gw.getWindowsWithTitle('Notepad'):
                            win.activate()
                            break
                    except Exception as e:
                        pass
                    
                    time.sleep(1.0)
                    vscode.vscode_type_code(explanation_text)"""
                    
code = code.replace(old_notepad, new_notepad)

with open(r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\src\jarvisx\agents\friday.py", "w") as f:
    f.write(code)

print("Friday focus logic updated.")
