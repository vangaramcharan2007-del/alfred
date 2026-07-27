import sys
import os

with open(r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\src\jarvisx\agents\friday.py", "r") as f:
    code = f.read()

# 1. Revert execution back to vscode_run_in_terminal (since vscode_controller is fixed to use Command Palette)
old_exec1 = """                    import os
                    os.system(f"start cmd /c \\"python {target_script1} & timeout 3\\"")
                    result1 = subprocess.run(["python", target_script1], capture_output=True, text=True)
                    
                    import time
                    time.sleep(1.0)
                    os.system(f"start cmd /c \\"python {target_script2} & timeout 3\\"")
                    result2 = subprocess.run(["python", target_script2], capture_output=True, text=True)"""

new_exec1 = """                    vscode.vscode_run_in_terminal(f"python {target_script1}")
                    result1 = subprocess.run(["python", target_script1], capture_output=True, text=True)
                    
                    vscode.vscode_run_in_terminal(f"python {target_script2}")
                    result2 = subprocess.run(["python", target_script2], capture_output=True, text=True)"""

code = code.replace(old_exec1, new_exec1)

old_exec2 = """                        result = subprocess.run(["python", os.path.join(target_path, "numpy_random.py")], capture_output=True, text=True)
                        os.system(f"start cmd /c \\"python {os.path.join(target_path, 'numpy_random.py')} & timeout 3\\"")"""

new_exec2 = """                        result = subprocess.run(["python", os.path.join(target_path, "numpy_random.py")], capture_output=True, text=True)
                        vscode.vscode_run_in_terminal(f"python {os.path.join(target_path, 'numpy_random.py')}")"""

code = code.replace(old_exec2, new_exec2)

# 2. Fix Notepad opening with bulletproof Popen + pygetwindow activate
old_notepad = """                    import os, time, pyautogui
                    # Use Win+R to forcefully open Notepad on Windows
                    pyautogui.hotkey("win", "r")
                    time.sleep(1.0)
                    pyautogui.write("notepad")
                    pyautogui.press("enter")
                    time.sleep(2.5) # Give it ample time to open and grab focus
                    vscode.vscode_type_code(explanation_text)"""
                    
new_notepad = """                    import subprocess, time
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

code = code.replace(old_notepad, new_notepad)

with open(r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\src\jarvisx\agents\friday.py", "w") as f:
    f.write(code)

print("Friday reverted to VS Code terminal + robust Notepad launch.")
